from djongo import models
from django.db import connection
 
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
    average_cycle_duration = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'search_patients'
        
    @staticmethod
    def calculate_average_cycle_durations():
        cursor = connection.cursor()
        pipeline = [
            {"$unwind": "$respiratory_data"},
            {"$unwind": "$respiratory_data.respiratory_cycles"},
            {"$group": {
                "_id": "$_id",
                "average_cycle_duration": {
                    "$avg": {
                        "$subtract": [
                            "$respiratory_data.respiratory_cycles.end_resp_cycle",
                            "$respiratory_data.respiratory_cycles.beginning_resp_cycle"
                        ]
                    }
                }
            }}
        ]
        cursor.execute(pipeline)
        results = cursor.fetchall()
        return results

class Diagnosis(models.Model):
    patient_id = models.ForeignKey(Patients, related_name='diagnoses', on_delete=models.CASCADE)
    diagnosis_name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'search_diagnosis'