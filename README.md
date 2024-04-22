# Respiratory-Diagnosis-Assistant

## About the Application

Specify the database system(s) and version(s)

## Installation Process

download the code

```
git clone https://github.com/nabinkim0318/Respiratory-Diagnosis-Assistant.git
```

pip install -r requirements.txt
<!-- pip install djongo -->
<!-- pip install django-storages -->


## Open Django Application

```
cd respiratory_diagnosis_assistant
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

open a search engine and go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## How to Search

**Search by Condition:** output the top 5 audio files which best match the condition and additional demographic information

**Search by Audio File:** output the condition and confidence score based on the audio file and additional demographic information

## Additional info needed to add to this documantation
Describe how to acquire project data. Include a small dataset sample (< 5 MB) or provide scripts to download/scrape/process the data.
How do we load this data into the database system?
Do you have some scripts to do that? If so, how do we execute them?
Did you use some tools for loading? If so, provide appropriate details and links.
If you are benchmarking different database systems, detail any configuration modifications made.
If generating your own data, include a sample of the synthetic dataset/database.


List third-party libraries required for code execution and provide installation instructions (e.g., through a requirements.txt file).
If applicable, explain how to run the GUI.
Include any other relevant information about running your application.