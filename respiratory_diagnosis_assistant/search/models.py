from djongo import models

class AudioFile(models.Model):
    file = models.FileField(upload_to='audio_files/')
    filename = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'search_audiofile'
    
class Patients(models.Model):
    patient = models.AutoField(primary_key=True)
    age = models.IntegerField()
    sex = models.CharField(max_length=10)
    adult_bmi = models.FloatField(null=True, blank=True)
    child_weight = models.FloatField(null=True, blank=True)
    child_height = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'search_patients'  # MongoDB collection name as specified

class RespiratoryData(models.Model):
    patient = models.ForeignKey(Patients, related_name='respiratory_data', on_delete=models.CASCADE)
    recording_index = models.IntegerField()
    chest_location = models.CharField(max_length=50)
    acquisition_model = models.CharField(max_length=50)
    recording_equipment = models.CharField(max_length=100)
    annotation_file = models.CharField(max_length=255)
    sound_file_path = models.CharField(max_length=255)

    class Meta:
        db_table = 'search_respiratory_data'  # MongoDB collection name as specified

class Diagnosis(models.Model):
    patient = models.ForeignKey(Patients, related_name='diagnoses', on_delete=models.CASCADE)
    diagnosis_name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'search_diagnosis'