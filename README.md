# GreenSpace
GreenSpace:  two-stage RF and CNN-based image classification models to identify 47 plant species. Implemented a user-friendly interface using Flask and RESTful APIs for seamless user interaction, and used Selenium for collecting plant information.

## Plant Care Web App Overview: 
This project is a final Ironhack BootCamp project. GreenSpace is designed to help users identify plants by image and provide customized care information such as watering, sunlight requirements, pruning schedules, and more. After plant recognition, the app fetches plant data from a JSON file and dynamically displays details in an easy-to-read format, including the plant's cycle, hardiness zone, and other essential care tips.

## Features
- User Authentication: Users will soon be able to create accounts and save their plant collections online.
- Plant Identification: Users can submit images to search for plants and view detailed plant information.
- Infographic Display: Care information, such as watering needs and sunlight requirements, is displayed in a visually appealing layout.
- Plant Collection: Users can save plants to their collection and manage them by adding custom names or nicknames.
- Custom Plant Suggestions: Users can submit plant names for future AI training if they do not find a match in the suggestions.
- User input for unrecognized plants: This feature allows users to manually add or suggest a plant species if the machine learning model fails to recognize the plant image they uploaded. The goal is to improve user interaction by giving them a way to contribute to the plant database. This feature will store user-provided species data in JSON file and can be reviewed and verified by administrators to improve the system's overall accuracy.


## Usage
- Search for Plants: Enter the plant name in the search bar, and the app will display the top matches.
- View Plant Care Info: For each plant, the app provides a detailed care guide based on the JSON data, including:
- Watering
- Sunlight
- Pruning schedules
- Hardiness zone
- Submit New Plants: If your plant isn't in the database, you can submit a new name for future inclusion.

## Future Improvements
- AI Integration for Disease Identification: Integration is a plant recognition AI that can automatically identify plant diseases from user-uploaded images.
- Mobile version
- Increasing number of available species

![Screenshot 2024-10-07 121718](https://github.com/user-attachments/assets/f900c0d8-1fdd-4457-a5c5-cc72971824d7)

![Screenshot 2024-10-07 121818](https://github.com/user-attachments/assets/f803138c-a4c3-4047-a8b6-d2925360360a)

![Screenshot 2024-10-07 122015](https://github.com/user-attachments/assets/6d317bef-051c-4f46-a573-e031022a2080)
