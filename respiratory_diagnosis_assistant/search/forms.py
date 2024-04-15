from django import forms
from .models import AudioFile

class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)
    audio_file = forms.FileField(label='Upload Audio', required=False)

    INPUT_CHOICES = (
        ('text', 'Text'),
        ('audio', 'Audio'),
    )
    input_type = forms.ChoiceField(choices=INPUT_CHOICES, widget=forms.RadioSelect())
