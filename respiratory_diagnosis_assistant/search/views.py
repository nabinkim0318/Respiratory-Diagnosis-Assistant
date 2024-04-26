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
        audio_file = request.FILES.get('audioFile')
        if audio_file:
            try:
                features = preprocess_audio(audio_file)
                prediction = gru_model.predict(np.array([features]))  # Model expects batch dimension
                predicted_scores = prediction.flatten()
                predicted_index = np.argmax(predicted_scores)
                predicted_condition = Diagnosis.objects.get(id=predicted_index)

                patients = Patients.objects.filter(diagnosis=predicted_condition).prefetch_related('respiratory_data')
                for patient in patients:
                    for resp in patient.respiratory_data:
                        results.append(prepare_metadata(patient, resp, predicted_condition, predicted_scores[predicted_index]))

                return render(request, 'search/audio_results.html', {'results': results})
            except Exception as e:
                messages.error(request, f"Error processing audio: {str(e)}")
            return render(request, 'search/audio_results.html', {'results': results})
        else:
            messages.error(request, 'No audio file provided')
            return render(request, 'search/audio_results.html', {'results': results})

    else:
        condition = request.POST.get('condition')
        matched_diagnoses = Diagnosis.objects.filter(diagnosis_name__icontains=condition).select_related('patient_id')
        for diag in matched_diagnoses:
            patient = diag.patient_id
            for resp in patient.respiratory_data:
                results.append(prepare_metadata(patient, resp, diag, None))

        return render(request, 'search/text_results.html', {'results': results})

def search(request):
    return render(request, 'search/search.html')

def prepare_metadata(patient, resp, diag, similarity_score=None):
    """ Helper function to prepare metadata dictionary. """
    print(resp)
    
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
        'respiratory_cycles': resp.get('respiratory_cycles'),
        'similarity_score': similarity_score if similarity_score is not None else "N/A"  # Display "N/A" if not applicable
    }

def preprocess_audio(audio_file):
    """
    Process the audio file to extract MFCC features as expected by the GRU model.
    """
    y, sr = librosa.load(audio_file, sr=None)  # Load audio file with its sample rate
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)  # Extract 13 MFCCs
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
