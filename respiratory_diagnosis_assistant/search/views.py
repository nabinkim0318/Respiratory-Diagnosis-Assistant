from django.shortcuts import render
from .forms import SearchForm
from .models import AudioFile, Patient, AudioRecording, Diagnosis
from django.http import JsonResponse
from .audio_utils import preprocess_audio, predict_from_features
import tensorflow as tf
from difflib import get_close_matches
import numpy as np

# Load the model on startup
model = tf.keras.models.load_model('gru_model.tf')

def home(request):
    return render(request, 'search/home.html')

def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST, request.FILES)
        if form.is_valid():
            input_type = form.cleaned_data['input_type']
            if input_type == 'text':
                query = form.cleaned_data['query']
                possible_diseases = Diagnosis.objects.values_list('disease', flat=True).distinct()
                close_matches = get_close_matches(query, possible_diseases, n=1, cutoff=0.6)
                
                if close_matches:
                    matched_diagnoses = Diagnosis.objects.filter(disease__iexact=close_matches[0]).select_related('patient')
                    search_results = [{
                        'patient_number': diag.patient.patient_number, 
                        'age': diag.patient.age, 
                        'sex': diag.patient.sex, 
                        'audio_file': record.patient.audiofile_set.first().file.url,
                        'disease': diag.disease, 
                        'diagnosis_id': diag.id}
                        for diag in matched_diagnoses
                    ]   
                else:
                    return render(request, 'search/search.html', {'form': form, 'message': 'No close matches found for your query.'})
            
            elif input_type == 'audio':
                audio_file = form.cleaned_data['audio_file']
                
                if not audio_file:
                    return JsonResponse({'error': 'No audio file provided'}, status=400)

                try:
                    features = preprocess_audio(audio_file)
                    prediction = predict_from_features(model, features)
                    disease_indices = np.where(prediction > 0.5)[1]  
                    predicted_diseases = [Diagnosis.objects.get(id=index) for index in disease_indices]

                    for disease in predicted_diseases:
                        similar_records = Diagnosis.objects.filter(disease=disease.disease).select_related('patient')
                        for record in similar_records:
                            search_results.append({
                                'patient_number': record.patient.patient_number,
                                'age': record.patient.age,
                                'sex': record.patient.sex,
                                'audio_file': record.patient.audiofile_set.first().file.url,
                                'disease': record.disease,
                                'similarity_score': float(prediction[0][disease.id])  
                            })
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=500)
            return render(request, 'search/result.html', {'search_results': search_results})
        else:
            return render(request, 'search/search.html', {'form': form})
    else:
        form = SearchForm()
    return render(request, 'search/search.html', {'form': form})

def convert_predictions_to_diseases(predictions):
    disease_names = ["COPD" ,"Bronchiolitis ", "Bronchiectasis", "Pneumoina", "URTI", "Healthy"]
    return [disease for idx, disease in enumerate(disease_names) if predictions[idx] > 0.75] 

def find_related_audios(diseases_predicted):
    return AudioFile.objects.filter(diagnosis__disease__in=diseases_predicted).select_related('diagnosis')

def about(request):
    return render(request, 'search/about.html')

def help(request):
    return render(request, 'search/help.html')

def contact(request):
    if request.method == 'POST':
        # Process feedback form submission
        feedback = request.POST.get('feedback')
        # Handle feedback submission (e.g., save to database)
        # For now, let's print the feedback to console
        print("Feedback:", feedback)
        return render(request, 'search/contact.html', {'message': 'Thank you for your feedback!'})
    else:
        return render(request, 'search/contact.html')
