from django.contrib import admin
from .models import AudioFile, Patients, RespiratoryData, Diagnosis

admin.site.register(AudioFile)
admin.site.register(Patients)
admin.site.register(RespiratoryData)
admin.site.register(Diagnosis)
