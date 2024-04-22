from django.shortcuts import render
from datetime import datetime
from .forms import SearchForm
from .models import Patients, RespiratoryData, Diagnosis
from django.http import JsonResponse
from .audio_utils import preprocess_audio, predict_from_features
import tensorflow as tf
from difflib import get_close_matches
import numpy as np
import boto3
from django.conf import settings

# Load the model on startup
model = tf.keras.models.load_model('gru_model.tf')

def home(request):
    return render(request, 'search/home.html')

def generate_presigned_url(object_name):
    s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    presigned_url = s3_client.generate_presigned_url('get_object',
                                                     Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                             'Key': object_name},
                                                     ExpiresIn=3600)
    return presigned_url

def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST, request.FILES)
        if form.is_valid():
            input_type = form.cleaned_data['input_type']
            search_results = []
            if input_type == 'text':
                query = form.cleaned_data['query']
                matched_diagnoses = Diagnosis.objects.filter(diagnosis_name__icontains=query).select_related('patient_id')
                for diag in matched_diagnoses:
                    patient = diag.patient_id
                    for resp in patient.respiratory_data:
                        search_results.append({
                            'patient_number': patient.patient_id,
                            'age': patient.age,
                            'sex': patient.sex,
                            'disease': diag.diagnosis_name,
                            'audio_file': f"https://respiratory-diagnosis.s3.us-east-2.amazonaws.com/{resp['sound_file_path']}",
                            'annotation_file': f"https://respiratory-diagnosis.s3.us-east-2.amazonaws.com/{resp['annotation_file']}",
                            'recording_index': resp['recording_index'],
                            'chest_location': resp['chest_location'],
                            'acquisition_model': resp['acquisition_model'],
                            'recording_equipment': resp['recording_equipment'],
                            'respiratory_cycles': resp['respiratory_cycles'],
                            'similarity_score': None  # Not applicable here
                        })
                for result in search_results:
                    result['annotation_file'] = generate_presigned_url(result['annotation_file'])
                    result['audio_file'] = generate_presigned_url(result['audio_file'])
                return render(request, 'search/result.html', {'search_results': search_results})

            elif input_type == 'audio':
                audio_file = request.FILES['audio_file']
                features = preprocess_audio(audio_file)
                prediction = predict_from_features(model, features)
                predicted_scores = np.squeeze(prediction)
                
                print(predicted_scores)
                predicted_indices = np.where(predicted_scores > 0.5)[0]
                predicted_diagnoses = Diagnosis.objects.filter(id__in=predicted_indices).select_related('patient_id')
                for diag in predicted_diagnoses:
                    patient = diag.patient_id
                    for resp in patient.respiratory_data:
                        search_results.append({
                            'patient_number': patient.patient_id,
                            'age': patient.age,
                            'sex': patient.sex,
                            'disease': diag.diagnosis_name,
                            'audio_file': f"https://respiratory-diagnosis.s3.us-east-2.amazonaws.com/{resp['sound_file_path']}",
                            'annotation_file': f"https://respiratory-diagnosis.s3.us-east-2.amazonaws.com/{resp['annotation_file']}",
                            'recording_index': resp['recording_index'],
                            'chest_location': resp['chest_location'],
                            'acquisition_model': resp['acquisition_model'],
                            'recording_equipment': resp['recording_equipment'],
                            'respiratory_cycles': resp['respiratory_cycles'],
                            'similarity_score': float(predicted_scores[diag.id])  # Assuming diag.id matches the index used in predictions
                        })
                for result in search_results:
                    result['annotation_file'] = generate_presigned_url(result['annotation_file'])
                    result['audio_file'] = generate_presigned_url(result['audio_file'])
                return render(request, 'search/result.html', {'search_results': search_results})                
        else:
            return render(request, 'search/search.html', {'form': form, 'message': 'Form is not valid. Please check your input.'})
    else:
        form = SearchForm()
        return render(request, 'search/search.html', {'form': form})
    
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