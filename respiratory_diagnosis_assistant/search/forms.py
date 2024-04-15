from django import forms
from .models import AudioFile

class SearchForm(forms.Form):
    query = forms.CharField(max_length=255, required=False, help_text="Enter a filename or leave blank for default naming.")
    audio_file = forms.FileField(required=False)
    input_type = forms.ChoiceField(choices=[('text', 'Text'), ('audio', 'Audio')])

    def clean(self):
        cleaned_data = super().clean()
        query = cleaned_data.get('query')
        audio_file = cleaned_data.get('audio_file')
        input_type = cleaned_data.get('input_type')

        if input_type == 'audio' and not audio_file:
            self.add_error('audio_file', 'This field is required for audio search.')

        if not query and not audio_file:
            raise forms.ValidationError('An audio file must be provided.')

        return cleaned_data