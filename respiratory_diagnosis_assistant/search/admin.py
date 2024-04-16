from django.contrib import admin
from .models import AudioFile, Patient, AudioRecording, Annotation, Diagnosis

admin.site.register(AudioFile)
admin.site.register(Patient)
admin.site.register(AudioRecording)
admin.site.register(Annotation)
admin.site.register(Diagnosis)
