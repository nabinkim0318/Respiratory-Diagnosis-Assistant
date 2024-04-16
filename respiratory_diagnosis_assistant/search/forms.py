from django import forms
from .models import AudioFile

class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=255, 
        required=False, 
        help_text="Enter disease or symptom information for text-based search."
    )
    audio_file = forms.FileField(
        required=False,
        help_text="Upload an audio file for audio-based search. Supported formats: .wav"
    )
    input_type = forms.ChoiceField(
        choices=[('text', 'Text'), ('audio', 'Audio')],
        help_text="Select 'Text' for text-based searches or 'Audio' for searches based on audio files."
    )

    def clean(self):
        cleaned_data = super().clean()
        query = cleaned_data.get('query')
        audio_file = cleaned_data.get('audio_file')
        input_type = cleaned_data.get('input_type')

        if input_type == 'audio':
            if not audio_file:
                self.add_error('audio_file', 'An audio file is required for audio search.')
            if not any(audio_file.name.endswith(ext) for ext in ['.wav', '.mp3']):
                self.add_error('audio_file', 'Invalid file type. Only .wav and .mp3 files are supported.')

        if input_type == 'text' and not query:
            self.add_error('query', 'A query is required for text search.')

        if not query and not audio_file:
            raise forms.ValidationError('Either a query for text search or an audio file for audio search must be provided.')

        return cleaned_data