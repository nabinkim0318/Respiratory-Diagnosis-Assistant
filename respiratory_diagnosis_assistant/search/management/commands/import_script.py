import csv
import pandas as pd
import os
from django.core.management.base import BaseCommand
from search.models import Patients, Diagnosis, RespiratoryData

class Command(BaseCommand):
    help = "Import patient and diagnosis data into MongoDB."

    def handle(self, *args, **options):
        self.import_patients()
        self.import_diagnoses()
        self.import_respiratory_data()

    def import_patients(self):
        df = pd.read_table("search\Respiratory_Sound_Database\demographic_info.txt", sep=' ', na_values=['NULL'])  
        for col in df:
            dt = df[col].dtype 
            if dt == int or dt == float:
                df.fillna({col:0}, inplace=True)
            else:
                df.fillna({col:""}, inplace=True)
        
        for _, row in df.iterrows():
            patient, created = Patients.objects.update_or_create(
                patient_id=int(row['patient_id']),
                age=int(row['age']),
                sex=row['sex'],
                adult_bmi=float(row['adult_bmi']),
                child_weight=float(row['child_weight']),
                child_height=float(row['child_height'])
            )

    def import_diagnoses(self):
        with open('search\Respiratory_Sound_Database\patient_diagnosis.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                patient_id = Patients.objects.get(patient_id=int(row['patient_id']))
                Diagnosis.objects.create(patient_id=patient_id, diagnosis_name=row['diagnosis_name'])

    def import_respiratory_data(self):
        files = os.listdir('search/Respiratory_Sound_Database/Audio_and_txt_files') 
        id = 0
        for file in files:
            if file.endswith(".txt"):
                path = f'search/Respiratory_Sound_Database/Audio_and_txt_files/{file}'
                df = pd.read_table(path, sep="\s+", header=None, 
                                   names=["beginning_resp_cycle", "end_resp_cycle", "crackles", "wheezes"],
                                   keep_default_na=False, na_values=None)
                df = df.drop(columns=['crackles', 'wheezes'])
                resp_cycles = df.to_dict("records")

                patient_id, recording_index, chest_location, acquisition_model, recording_equipment = file.split('_')
                patient = Patients.objects.get(patient_id=int(patient_id))
                
                if patient.respiratory_data is None:
                    patient.respiratory_data = []

                respiratory_data_instance = {
                    'id': id,
                    'recording_index': recording_index,
                    'chest_location': chest_location,
                    'acquisition_model': acquisition_model,
                    'recording_equipment': recording_equipment,
                    'annotation_file': file,
                    'respiratory_cycles': resp_cycles,
                    'sound_file_path': f"{file[:-4]}.wav"
                }
                
                patient.respiratory_data.append(respiratory_data_instance)
                patient.save()
                
                id += 1