from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from pydub import AudioSegment
from .forms import SearchForm
import os
from .models import AudioFile



def home(request):
    return render(request, 'search/home.html')

def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST, request.FILES)
        if form.is_valid():
            query = form.cleaned_data['query']
            input_type = form.cleaned_data['input_type']
            if input_type == 'text':
                # Handle text search
                pass
            elif input_type == 'audio':
                audio_file = form.cleaned_data['audio_file']
                try:
                    # Check if the file is not empty
                    if audio_file.size == 0:
                        raise ValidationError("Empty audio file")

                    # Check file extension
                    ext = os.path.splitext(audio_file.name)[1]
                    if ext.lower() not in ['.mp3', '.wav']:
                        raise ValidationError("Invalid file format, only .mp3 and .wav are allowed")

                    # Optional: Check audio duration - This requires analyzing the file, possibly with a library like pydub
                    audio = AudioSegment.from_file(audio_file)
                    duration_seconds = len(audio) / 1000
                    if duration_seconds < 10 or duration_seconds > 90:
                        raise ValidationError("Audio file must be between 10 and 90 seconds")

                    AudioFile.objects.create(file=audio_file)
                    # Continue with existing process

                except ValidationError as e:
                    return render(request, 'search/search.html', {'form': form, 'error_message': str(e)})
                
                
            search_results = [
                {'audio_file': 'audio1.mp3', 'metadata': {'patient_id': '123', 'diagnosis': 'Asthma'}, 'similarity_score': 0.75},
                {'audio_file': 'audio2.mp3', 'metadata': {'patient_id': '456', 'diagnosis': 'Bronchitis'}, 'similarity_score': 0.85},
            ]
            return render(request, 'search/result.html', {'search_results': search_results})
    else:
        form = SearchForm()
    return render(request, 'search/search.html', {'form': form})

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
