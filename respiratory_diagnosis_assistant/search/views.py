from django.shortcuts import render
from datetime import datetime
from .models import Patients, RespiratoryData, Diagnosis
from .audio_utils import preprocess_audio
import numpy as np
import boto3
from django.conf import settings
import keras
import librosa
from django.contrib import messages
from django.http import HttpResponse
import os
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['your_database']
collection = db['your_collection']

# Load the model on startup
gru_model = keras.models.load_model('gru_model.keras')

# S3 Bucket configuration
s3_client = boto3.client('s3')
bucket_name = 'respiratory-diagnosis'

def home(request):
    return render(request, 'search/home.html')

def submit(request):
    print("Request method:", request.method)
    print("Request POST data:", request.POST)
    print("Request FILES data:", request.FILES)
    search_type = request.POST.get('searchType')
    results = []

    if search_type == 'audio':
        # TODO: code for getting meta data from the user, if any, append it in the results  
        # TODO: (testing) handle audio_results.html so that it handles okay when there are no meta data
        # TODO: mp3 wav check, length check 
        # TODO: only save the audio file when the accuracy score is greater than 70%
        audio_file = request.FILES.get('audioFile')
        if audio_file:
            try:       
                # preprocess meta data in the results dictionary 
                result = prepare_metadata_user_input(request) 
                
                # prepare for the input for the pretrained model     
                features = preprocess_audio(audio_file)
                print(f"features: ", features)
                reshaped_features = features.reshape(1, 1, len(features))
                print(f"reshaped_features: ", reshaped_features)
                prediction = gru_model.predict(reshaped_features)  # Model expects batch dimension
                print(f"Prediction: ", prediction)
                predicted_scores = prediction.flatten()
                predicted_index = np.argmax(predicted_scores)
                c_names = ['COPD', 'Bronchiolitis', 'Bronchiectasis', 'Pneumonia', 'Healthy', 'URTI']
                predicted_condition = c_names[predicted_index]
                print(f"predicted_condition: ", predicted_condition)
                
                # save user audio in the media folder 
                audio_file_url = save_user_audio(audio_file)
                
                # append audio_file_url and classification in the results 
                result['audio_file_url'] = audio_file_url
                result['predicted_condition'] = predicted_condition
                results.append(result)
                print("results:", results)
                return render(request, 'search/audio_results.html', {'results': results, 'audio_file_url': audio_file_url})
            except Exception as e:
                messages.error(request, f"Error processing audio: {str(e)}")
            return render(request, 'search/audio_results.html', {'results': results})
        else:
            messages.error(request, 'No audio file provided')
            return render(request, 'search/audio_results.html', {'results': results})

    else:
        print("Not audio condition")
        print(request)
        condition = request.POST.get('condition')
        metadata_variables = prepare_metadata_user_input(request) 
        
        matched_diagnoses = Diagnosis.objects.filter(diagnosis_name__icontains=condition).select_related('patient_id')
        patient_ids = [diag.patient_id_id for diag in matched_diagnoses]
        print(f"patient_ids: ", patient_ids)
        patients = Patients.objects.filter(patient_id__in=patient_ids)
        print(f"patients: ", patients)
        
        for pat in patients:
            # Get the patient associated with the diagnosis
            score = calculate_score(pat, metadata_variables)
            # Append patient and score to results list
            results.append({'patient': pat, 'score': score})

        # Sort the results based on the score in descending order
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        print(f"sorted_results: ", sorted_results)

        # Prepare metadata for sorted patients and append to final_results list
        final_results = []

        for result in sorted_results:
            patient = result['patient']
            for resp in patient.respiratory_data:
                final_results.append(prepare_metadata_text(patient, resp, condition, None))
        #print(f"final_results: ", final_results)
        #print(f"final results len ", len(final_results))
        return render(request, 'search/text_results.html', {'results': final_results})


def search(request):
    return render(request, 'search/search.html')

def save_user_audio(audio_file):
    # Save the uploaded audio file to a temporary location
    audio_file_path = os.path.join(settings.MEDIA_ROOT,'audio_files', audio_file.name)
    if not os.path.exists(os.path.dirname(audio_file_path)):
        os.makedirs(os.path.dirname(audio_file_path))
        
    with open(audio_file_path, 'wb') as destination:
        for chunk in audio_file.chunks():
            destination.write(chunk)
    audio_file_url = audio_file_url = os.path.join(settings.MEDIA_URL, 'audio_files', audio_file.name)
    print(f"audio_file_url: ", audio_file_url)
    return audio_file_url
    
def prepare_metadata_user_input(request):
    # Get the demographic information from the form
    age = request.POST.get('age')
    sex = request.POST.get('sex')
    adult_bmi = request.POST.get('bmi')
    child_weight = request.POST.get('childWeight')
    child_height = request.POST.get('childHeight')
    
    results = {
        'age': age,
        'sex': sex,
        'adult_bmi': adult_bmi,
        'child_weight': child_weight,
        'child_height': child_height
    }
    return results

def calculate_score(patient, metadata_variables):
    score = 0
    # Check each metadata variable and increment the score if it matches the condition
    for variable, value in metadata_variables.items():
        if value:
            if variable == 'age':
                age_difference = abs(patient.age - int(value))
                # Calculate the score based on the inverse of the age difference
                age_score = max(0, 1 - age_difference / 100)
                score += age_score
        elif str(getattr(patient, variable)) == str(value):
            print(variable, value)
            score += 1

    print(f"patien t: ", patient)
    print(f"score: ", score)
    return score
 
def prepare_metadata_text(patient, resp, condition, similarity_score=None):
    """ Helper function to prepare metadata dictionary. """
    print(resp)

    cycles = ""
    for cycle in resp.get('respiratory_cycles'):
        cycles += str(cycle.get('beginning_resp_cycle')) + "~" + str(cycle.get('end_resp_cycle')) + " | "
    
    return {
        'patient_number': patient.patient_id,
        'age': patient.age,
        'sex': patient.sex,
        'disease': condition,
        'adult_bmi': patient.adult_bmi,
        'child_height': patient.child_height,
        'child_weight': patient.child_weight,
        'audio_file': f"https://respiratory-diagnosis.s3.us-east-2.amazonaws.com/{resp.get('sound_file_path')}",
        'annotation_file': f"https://respiratory-diagnosis.s3.us-east-2.amazonaws.com/{resp.get('annotation_file')}",
        'recording_index': resp.get('recording_index'),
        'chest_location': resp.get('chest_location'),
        'acquisition_model': resp.get('acquisition_model'),
        'recording_equipment': resp.get('recording_equipment'),
        'respiratory_cycles': cycles,
        'similarity_score': similarity_score if similarity_score is not None else "N/A"  # Display "N/A" if not applicable
    }

def preprocess_audio(audio_file):
    """
    Process the audio file to extract MFCC features as expected by the GRU model.
    """
    y, sr = librosa.load(audio_file, sr=None)  # Load audio file with its sample rate
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=52)  # Extract 13 MFCCs
    mfccs_processed = np.mean(mfccs.T, axis=0)  # Average over frames
    return mfccs_processed


def about(request):
    return render(request, 'search/about.html')

def help(request):
    return render(request, 'search/help.html')

def contact(request):
    if request.method == 'POST':
        feedback = request.POST.get('feedback')
        if feedback:
            save_feedback(feedback)
            return render(request, 'search/contact.html', {'message': 'Thank you for your feedback!'})
        else:
            return render(request, 'search/contact.html', {'error': 'Please provide feedback before submitting.'})
    else:
        return render(request, 'search/contact.html')

def save_feedback(feedback):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('feedback.txt', 'a') as file:
        file.write(f"{timestamp}: {feedback}\n")
