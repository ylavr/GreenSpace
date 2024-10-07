import pickle
from flask import request
from PIL import Image
import numpy as np
import cv2
import json
import matplotlib.image as mpimg
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image


#image_path = r'test_images\images (4).jpg'
image_path = r'test_images\anthurium.jpg'
#image_path = r'test_images\download.jpg'
model_path = r'saved_models\rf_classifier_model.pkl'

### Prediction first_stage:

# Function to predict the class of a test image
def predict_image_class(model, image_path):
    """
    Predicts the class of the given image using the provided model.

    Parameters:
    - model: The trained machine learning model.
    - image_path: Path to the image file.

    Returns:
    - The predicted class label.
    """
    features = extract_features(image_path)
    if features is None:
        return None
    features = features.reshape(1, -1)  # Reshape for a single sample
    prediction = model.predict(features)
    return prediction[0]

# Function to load the saved model
def load_model(filename='rf_classifier_model.pkl'):
    """
    Loads the saved model from a file using pickle.

    Parameters:
    - filename: The name of the file to load the model from.

    Returns:
    - The loaded machine learning model.
    """
    with open(filename, 'rb') as file:
        model = pickle.load(file)
    #print(f"Model loaded from {filename}")
    return model


# Function to extract color histogram features
def extract_features(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Image not found or corrupted: {image_path}")
        return None
    image = cv2.resize(image, (256, 256))  # Resize image to a fixed size
    # Convert image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Extract color histograms for each channel (R, G, B)
    hist_r = cv2.calcHist([image_rgb], [0], None, [256], [0, 256]).flatten()
    hist_g = cv2.calcHist([image_rgb], [1], None, [256], [0, 256]).flatten()
    hist_b = cv2.calcHist([image_rgb], [2], None, [256], [0, 256]).flatten()
    
    # Concatenate the histograms into a single feature vector
    hist_features = np.concatenate([hist_r, hist_g, hist_b])
    
    return hist_features


def prediction_class(model_path, image_path):
    try:
        model = load_model(model_path)
        if model is not None:
            predicted_class = predict_image_class(model, image_path)
            if predicted_class is not None:

                return predicted_class
            else:
                print("Failed to predict the class of the test image.")
        else:
            print("Model loading failed.")
    except Exception as e:
        print(f"An error occurred: {e}")

category_result = prediction_class(model_path, image_path)
#print(category_result)

###Prediction second stage:


def prediction_species(category_result, img_path):
    """
    Predicts the species of the plant given an image and a category result.

    Parameters:
    - category_result: The category result (0 or 1).
    - img_path: The path to the image file.

    Returns:
    - predicted_label: The predicted species label.
    """
    # Load the appropriate model and class indices based on the category result
    if category_result == 0:
        model = tf.keras.models.load_model('my_model_flowering_128_for_project.keras')
        class_indices_file = 'class_indices_flowering.json'
    elif category_result == 1:
        model = tf.keras.models.load_model('my_model_foliage_128_last.keras')
        class_indices_file = 'class_indices_foliage.json'
    elif category_result == 2:
        model = tf.keras.models.load_model('my_model_palms_and_ferns_128_for_project.keras')
        class_indices_file = 'class_indices_palms_and_ferns.json'
    elif category_result == 3:
        model = tf.keras.models.load_model('my_model_succulents_and_cacti_128_for_project.keras')
        class_indices_file = 'class_indices_succulents_and_cacti.json'
    else:
        print("Invalid category result. Must be 0 (flowering) or 1 (foliage), 2 (palms_and_ferns) or 3 (succulents_and_cacti).")
        return None

    # Load the class indices from the JSON file
    with open(class_indices_file, 'r') as f:
        indices_to_labels = json.load(f)

    # Convert string keys to integers
    indices_to_labels = {int(k): v for k, v in indices_to_labels.items()}

    img_size = 128  # the input size of model

    # Load and preprocess the image
    img = image.load_img(img_path, target_size=(img_size, img_size))
    img_array = image.img_to_array(img) / 255.0  # Normalize the image
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension

    # Make a prediction
    prediction = model.predict(img_array)

    # Get the index of the predicted class
    predicted_class_idx = np.argmax(prediction, axis=1)[0]

    # Map the predicted class index to the class label
    predicted_label = indices_to_labels[predicted_class_idx]

    #print(f"Predicted label: {predicted_label}")

    # Get the top 3 predictions
    top_3_indices = np.argsort(prediction[0])[-3:][::-1]  # Indices of top 3 probabilities
    top_3_probs = prediction[0][top_3_indices]
    top_3_labels = [indices_to_labels[idx] for idx in top_3_indices]

    class_labels = indices_to_labels.values()
    # Initialize an empty dictionary to store the mapping of class labels to image paths
    class_label_to_image_path = {}
    base_dir = 'house_plant_species'

    #Loop through each class label and find an image for each label in the base directory
    for label in class_labels:
        label_dir = os.path.join(base_dir, label)
        if os.path.exists(label_dir):
            found_image = False
            for file_name in os.listdir(label_dir):
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(label_dir, file_name)
                    class_label_to_image_path[label] = image_path
                    found_image = True
                    break
            if not found_image:
                class_label_to_image_path[label] = None  # No image found
        else:
            class_label_to_image_path[label] = None  # Directory not found

    # Prepare the result to return
    top_3_results = []
    for i in range(3):
        label = top_3_labels[i]
        result = {
            "label": label,
            "probability": round(top_3_probs[i] * 100, 2),  # Convert to percentage
            "image_path": class_label_to_image_path.get(label, None),
            "category": category_result
        }
        top_3_results.append(result)

    # Return the top 3 predictions with their probabilities and image paths
    # print (top_3_results) 
    return top_3_results 
     
prediction_species(category_result,image_path)

#Offering funny_names:
def get_funny_plant_names(category_result):
    flowering_names = [
        "Queen Chlorissa", "Duchess Dandelion", "The Blossom Bandit", "Bella Thorn",
        "Blue Ivy", "Flaura Croft", "Kate Moss", "Megan Thee Plant", "Pineapple Princess",
        "The Mighty Thistle", "The Golden Girls", "Cosmo and Wanda", "Destiny's Child", "The Supremes"
    ]
    
    palms_and_ferns_names = [
        "General Greenthumb", "Morgan Treeman",
        "Fernie Sanders", "Christofern", "Shrek",  "Oompa Loompa",
        "Tree Diddy", "Woody", "Bonnie and Clyde", "Carrie, Miranda, Samantha and Charlotte",
        "The Fantastic Four", "Jennifer Aniston, Lisa Could-Grow, and Courtney Pots"
    ]
    
    succulents_and_cacti_names = [
        "The Notorious B.U.D.", "Sir Pokes-a-Lot", "Cactus Everdeen",
        "Spike Leaf", "Mr. Prickles", "Fluffy", "The Thorninator", "Sir Sprouts-a-Lot", "Spice Girls", "Elvis Parsley",  "Count Plantula"
    ]
    
    foliage_names = [
        "Leafy McLeafFace", "Shrek","Oompa Loompa", "Planty McPlantface", "Count Creeper", "Dobby the Houseplant",
        "Woody (indoor tree)", "Tony the Tiger", "Snake Gyllenhaal", "President Plant",
        "Rooty McRootface", "The Shrubinator", "Basil the Brave", "Bill (money plant)",
        "Lil Plant", "Mr. Plant", "Mrs. Plant", "Pokey","Lord of the Leaves","Professor Chlorophyll","Captain Greenbeard", "Dr. Plant", "Vincent Van Grow", "The Great Greenini",
    ]
    
    if category_result == '0':
        return flowering_names
    elif category_result == '1':
        return foliage_names
    elif category_result == '2':
        return palms_and_ferns_names
    elif category_result == '3':
        return succulents_and_cacti_names
    else:
        return []

def recognize_plant(file_path):
    model_path = r'saved_models\rf_classifier_model.pkl'
    category_result = prediction_class(model_path, file_path)
    return prediction_species(category_result,file_path)