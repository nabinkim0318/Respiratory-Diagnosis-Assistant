from django.db import models

class AudioFile(models.Model):
    file = models.FileField(upload_to='audio_files/')
    filename = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
class Patient(models.Model):
    patient_number = models.IntegerField(unique=True)
    age = models.IntegerField()
    sex = models.CharField(max_length=10)
    bmi = models.FloatField(null=True, blank=True)
    child_weight = models.FloatField(null=True, blank=True)
    child_height = models.FloatField(null=True, blank=True)

class AudioRecording(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    recording_index = models.IntegerField()
    chest_location = models.CharField(max_length=100)
    acquisition_mode = models.CharField(max_length=100)
    recording_equipment = models.CharField(max_length=100)
    file_path = models.CharField(max_length=200)

class Annotation(models.Model):
    audio_recording = models.ForeignKey(AudioRecording, on_delete=models.CASCADE)
    begin_cycle = models.FloatField()
    end_cycle = models.FloatField()
    crackles = models.BooleanField()
    wheezes = models.BooleanField()

class Diagnosis(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    disease = models.CharField(max_length=100)