from django.shortcuts import render
from datetime import datetime
from .forms import SearchForm
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
                # Handle audio file upload
                audio_file = form.cleaned_data['audio_file']
                AudioFile.objects.create(file=audio_file)
                # Process audio file
                pass
            # For now, let's assume we have some dummy search results
            search_results = [
                {'audio_file': 'audio1.mp3', 'metadata': {'patient_id': '123', 'diagnosis': 'Asthma'}, 'similarity_score': 0.75},
                {'audio_file': 'audio2.mp3', 'metadata': {'patient_id': '456', 'diagnosis': 'Bronchitis'}, 'similarity_score': 0.85},
            ]
            return render(request, 'search/result.html', {'search_results': search_results})
    else:
        form = SearchForm()
    return render(request, 'search/search.html', {'form': form})

def text_results(request):
    # Add your view logic here
    return render(request, 'search/text_results.html') 

def audio_results(request):
    # Add your view logic here
    return render(request, 'search/audio_results.html') 

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