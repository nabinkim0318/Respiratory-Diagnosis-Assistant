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
        # code for getting meta data from the user, if any, append it in the results  
        # (testing) handle audio_results.html so that it handles okay when there are no meta data
        # mp3 wav check, length check 
        # only save the audio file when the accuracy score is greater than 70%
        audio_file = request.FILES.get('audioFile')
        if audio_file:
            try:       
                result = prepare_metadata_audio(request)     
                features = preprocess_audio(audio_file)
                print(f"features: ", features)
                reshaped_features = features.reshape(1, 1, len(features))
                print(f"reshaped_features: ", reshaped_features)
                
                # Save the uploaded audio file to a temporary location
                audio_file_path = os.path.join(settings.MEDIA_ROOT,'audio_files', audio_file.name)
                if not os.path.exists(os.path.dirname(audio_file_path)):
                    os.makedirs(os.path.dirname(audio_file_path))
                    
                with open(audio_file_path, 'wb') as destination:
                    for chunk in audio_file.chunks():
                        destination.write(chunk)
                        
                audio_file_url = audio_file_url = os.path.join(settings.MEDIA_URL, 'audio_files', audio_file.name)
                print(f"audio_file_url: ", audio_file_url)
                
                prediction = gru_model.predict(reshaped_features)  # Model expects batch dimension
                print(f"Prediction: ", prediction)
                predicted_scores = prediction.flatten()
                predicted_index = np.argmax(predicted_scores)
                c_names = ['Bronchiectasis', 'Bronchiolitis', 'COPD', 'Healthy', 'Pneumonia', 'URTI']
                predicted_condition = c_names[predicted_index]
                print(f"predicted_condition: ", predicted_condition)
                print("Results:", result)
                
            
                result['audio_file_url'] = audio_file_url
                result['predicted_condition'] = predicted_condition
                print("Results:", result)
                print("HAPSFPDA")
                results.append(result)
                return render(request, 'search/audio_results.html', {'results': results, 'audio_file_url': audio_file_url})
            except Exception as e:
                messages.error(request, f"Error processing audio: {str(e)}")
            return render(request, 'search/audio_results.html', {'results': results})
        else:
            messages.error(request, 'No audio file provided')
            return render(request, 'search/audio_results.html', {'results': results})

    else:
        print("Not audio condition")
        condition = request.POST.get('condition')
        matched_diagnoses = Diagnosis.objects.filter(diagnosis_name__icontains=condition).select_related('patient_id')
        print(f"matched_diagnoses: ", matched_diagnoses)
        for diag in matched_diagnoses:
            print(f"diag: ", diag)
            patient = diag.patient_id
            print(f"patient: ", patient)
            for resp in patient.respiratory_data:
                results.append(prepare_metadata_text(patient, resp, diag, None))
                print(f"resp: ", resp)
        print("Results:", results)
        return render(request, 'search/text_results.html', {'results': results})

def search(request):
    return render(request, 'search/search.html')

def prepare_metadata_audio(request):
    # Get the demographic information from the form
    age = "Not specified" if request.POST.get('age') == '' else request.POST.get('age')
    sex = "Not specified" if not request.POST.get('sex') else request.POST.get('sex')
    bmi = "Not specified" if request.POST.get('bmi') == '' else request.POST.get('bmi')
    child_weight = "Not specified" if request.POST.get('childWeight') == '' else request.POST.get('childWeight')
    child_height = "Not specified" if request.POST.get('childHeight') == '' else request.POST.get('childHeight')
    
    results = {
        'age': age,
        'sex': sex,
        'bmi': bmi,
        'child_weight': child_weight,
        'child_height': child_height
    }
    return results

def prepare_metadata_text(patient, resp, diag, similarity_score=None):
    """ Helper function to prepare metadata dictionary. """
    print(resp)

    cycles = ""
    for cycle in resp.get('respiratory_cycles'):
        cycles += str(cycle.get('beginning_resp_cycle')) + "~" + str(cycle.get('end_resp_cycle')) + " | "
    
    return {
        'patient_number': patient.patient_id,
        'age': patient.age,
        'sex': patient.sex,
        'disease': diag.diagnosis_name,
        'audio_file': f"https://respiratory-diagnosis.s3.us-east-2.amazonaws.com/{resp.get('sound_file_path')}",
        'annotation_file': f"https://respiratory-diagnosis.s3.us-east-2.amazonaws.com/{resp.get('annotation_file')}",
        'recording_index': resp.get('recording_index'),
        'chest_location': resp.get('chest_location'),
        'acquisition_model': resp.get('acquisition_model'),
        'recording_equipment': resp.get('recording_equipment'),
        'respiratory_cycles': cycles,
        'average_cycle': patient.average_cycle_duration,
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
