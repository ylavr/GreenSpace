from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session, send_from_directory
from flask_wtf import FlaskForm
import bcrypt
import json
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
import secrets
from datetime import timedelta
import os
from functions import *


app = Flask(__name__)
secret_key = secrets.token_hex(16)  # Generates a 16-byte hex string
app.config['SECRET_KEY'] = secret_key  # Required for using forms and sessions

# Path to the JSON file for storing user data
USER_DATA_FILE = 'user_data.json'

# Helper function to load user data from the JSON file
def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # If file doesn't exist, return an empty dictionary
        return {}
    except json.JSONDecodeError as e:
        print(f"Error loading JSON data: {e}")
        return {}

# Helper function to save user data to the JSON file
def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Registration Form (if you want account creation)
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Create Account')

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
   
    if 'username' in session:
        # User is logged in, skip login page and redirect to main page
        return redirect(url_for('main_page'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user_data = load_user_data()
        username = form.username.data
        password = form.password.data.encode('utf-8')

        if username in user_data:
            hashed_password = user_data[username]['password'].encode('utf-8')
            if bcrypt.checkpw(password, hashed_password):
                # Store username in session
                session['username'] = username
                # Make the session permanent
                session.permanent = True
                app.permanent_session_lifetime = timedelta(minutes=30)  # Session lasts for 30 minutes              
                flash(f'Login successful for {username}!', 'success')
                return redirect(url_for('main_page'))
            else:
                flash('Invalid username or password', 'danger')
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    # Clear the session to log out the user
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_data = load_user_data()
        username = form.username.data
        password = form.password.data.encode('utf-8')

        # Check if the username already exists
        if username in user_data:
            flash(f'Username {username} is already taken, please choose a different one.', 'danger')
        else:
            # Hash the password before saving
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

            # Save the new user data in the JSON file
            user_data[username] = {
                'password': hashed_password.decode('utf-8')
            }
            save_user_data(user_data)

            flash(f'Account created for {username}!', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)

# Set the directory where the images are stored (outside static folder)
IMAGE_FOLDER = os.path.join(os.getcwd(), 'house_plant_species')

@app.route('/image/<path:filename>')
def serve_image(filename):
    # Serve the image from the house_plant_species folder
    return send_from_directory(IMAGE_FOLDER, filename)

#Run recognizing function
@app.route('/recognize', methods=['POST'])
def recognize():
    # Check if the file is part of the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the file temporarily
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    # Call Python function to process the image
    results = recognize_plant(file_path)  

    #Adjust image paths to show them on result page
    for result in results:
        path = result.get('image_path')
        path = path.replace('house_plant_species\\', '')
        path = path.replace('\\', '/')
        result['image_path'] = url_for('serve_image', filename=path)
        result['category'] = int(result['category'])

    # Return the results as JSON
    print(results)
    return jsonify(results)

PLANTS_CATALOG = 'corrected_species_data.json'
USER_PLANTS = 'user_plants.json'

def read_user_plants():
    try:
        with open(USER_PLANTS, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # If file doesn't exist, return an empty dictionary
        return {}
    except json.JSONDecodeError as e:
        return {}    

# Save the JSON file with updated user plants
def save_user_plants(data):
    with open(USER_PLANTS, 'w') as file:
        json.dump(data, file, indent=4)

# Route to add plant to user's plant list
@app.route('/add_plant', methods=['POST'])
def add_plant():    
    data = request.get_json()
    print(data)
    username = session['username']
    plants_data = load_plant_data()
    for key, value in plants_data.items():
        if value.get('mapping_name') == data.get('name'):
            plant_name = key
    plant_image = data.get('image')
    plant_nickname = data.get('nickname')

    # Load the existing user plants
    user_plants = read_user_plants()

    # Add plant to the user's list
    if username not in user_plants:
        user_plants[username] = []
    
    # Add plant to user's list if it doesn't already exist
    user_plants[username].append({
        'name': plant_name,
        'image': plant_image,
        'nickname': plant_nickname
    })

    # Save the updated list
    save_user_plants(user_plants)

    return jsonify({"success": True, "message": f"Plant {plant_name} added successfully!"})

# Load plant data from the corrected_species_data.json file
def load_plant_data():
    with open('corrected_species_data.json', 'r') as file:
        return json.load(file)
# Route to fetch plant details
@app.route('/plant_details/<plant_name>', methods=['GET'])
def plant_details(plant_name):
    plant_data = load_plant_data()

    # Find plant details by plant_name
    plant_info = plant_data.get(plant_name)
    
    if plant_info:
        print (jsonify({
            "success": True,
            "description": plant_info.get('description', {}),
            "details": plant_info.get('details', {}),
            "care_info": plant_info.get('care_info', {})
        }))
        return jsonify({
            "success": True,
            "description": plant_info.get('description', {}),
            "details": plant_info.get('details', {}),
            "care_info": plant_info.get('care_info', {})
        })
    else:
        return jsonify({"success": False, "message": "Plant not found"}), 404
    
@app.route('/submit_plant_name', methods=['POST'])
def submit_plant_name():
    print('SUBMIT_PLANT_NAME STARTED')
    data = request.get_json()
    plant_name = data.get('plant_name')

    if plant_name:
        # Here, save the plant name for future AI training, for example, storing it in a file.
        with open('submitted_plants.json', 'a') as file:
            file.write(json.dumps({"plant_name": plant_name}) + "\n")
        
        return jsonify({"success": True, "message": "Plant name submitted successfully."})
    else:
        return jsonify({"success": False, "message": "Plant name is required."}), 400

# Route to load predefined nicknames
@app.route('/get_nicknames/<category>')
def get_nicknames(category):    
    print ( f"\033[31mGET_NICKNAMES started\033[0m" )
    print ( f"\033[31m{get_funny_plant_names(category)}\033[0m" )
    return jsonify(get_funny_plant_names(category))

# Route for main page (index.html)
@app.route('/main')
def main_page():
    if 'username' in session:  # Check if the user is logged in by checking if the username is stored in the session
        username = session['username']  # Retrieve the username from the session
        user_plants = read_user_plants( )
        plants = user_plants.get(username)  # Fetch plants for the user 
        return render_template('index.html', username=username, plants=plants)
    else:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))

@app.route('/')
def home():
    return redirect(url_for('login'))  # Redirect to /login

if __name__ == '__main__':
    app.run(debug=True)