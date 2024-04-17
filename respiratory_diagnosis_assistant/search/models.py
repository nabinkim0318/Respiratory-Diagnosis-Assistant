from djongo import models

class AudioFile(models.Model):
    file = models.FileField(upload_to='audio_files/')
    filename = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'search_audiofile'
    
class RespiratoryData(models.Model):
    id = models.IntegerField(primary_key=True)
    recording_index = models.CharField(max_length=3)
    chest_location = models.CharField(max_length=2)
    acquisition_model = models.CharField(max_length=2)
    recording_equipment = models.CharField(max_length=20)
    annotation_file = models.CharField(max_length=255)
    respiratory_cycles = models.JSONField()  # Using JSONField to store array data
    sound_file_path = models.CharField(max_length=255)


class Patients(models.Model):
    patient_id = models.AutoField(primary_key=True)
    age = models.IntegerField()
    sex = models.CharField(max_length=10)
    adult_bmi = models.FloatField(null=True, blank=True)
    child_weight = models.FloatField(null=True, blank=True)
    child_height = models.FloatField(null=True, blank=True)
    respiratory_data = models.ArrayField(
        model_container=RespiratoryData,
        null=True, blank=True
    )

    class Meta:
        db_table = 'search_patients'

class Diagnosis(models.Model):
    patient_id = models.ForeignKey(Patients, related_name='diagnoses', on_delete=models.CASCADE)
    diagnosis_name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'search_diagnosis'