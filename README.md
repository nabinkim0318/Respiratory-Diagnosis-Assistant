# Respiratory Diagnosis Assistant

## About the Application

The Respiratory Diagnosis Assistant is a tool designed to assist in diagnosing respiratory conditions based on audio recordings. It utilizes Amazon S3 for storing audio files and MongoDB for managing data.

## Database Systems and Versions

- **Amazon S3**: Used for storing audio files. For information on how to set up and use Amazon S3, please refer to the [official documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html).
- **MongoDB Atlas**: Used for managing data. The application is configured to connect to a MongoDB Atlas cluster running version 7.0.8. For more information on MongoDB Atlas and how to set it up, please refer to the [official documentation](https://docs.atlas.mongodb.com/).

## Installation Process

### Prerequisites
- Python version 3.11 or higher
- Access to MongoDB (Contact mkim925@gatech.edu for access)

### Installation Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/nabinkim0318/Respiratory-Diagnosis-Assistant.git
    ```

2. Navigate to the project directory and create a virtual environment:

    ```bash
    cd Respiratory-Diagnosis-Assistant
    python -m venv venv
    ```

3. Activate the virtual environment:
   
   - macOS:
     ```bash
     source venv/bin/activate
     ```
   - Windows:
     ```bash
     venv\Scripts\activate
     ```

4. Install required libraries:

    ```bash
    pip install -r requirements.txt
    ```

5. Run the Django application:

    ```bash
    python manage.py runserver
    ```

6. Open a web browser and go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to access the application.

## How to Search

### Search by Condition

This option outputs the top 5 audio files that best match the provided condition, along with additional demographic information.

### Search by Audio File

This option outputs the condition and confidence score based on the provided audio file, along with additional demographic information.

## Additional Information

- **Sample Dataset**: A small dataset sample is located in the directory `Respiratory-Diagnosis-Assistant/respiratory_diagnosis_assistant/media/audio_files`.
- **Data Loading Scripts**: Scripts to load data into the MongoDB database are available:

    ```bash
    python manage.py import_script  # load dataset into MongoDB
    python manage.py average_calc   # calculate average cycle duration
    ```

Please note that you do not need to run these scripts as the data are already loaded into the system.
