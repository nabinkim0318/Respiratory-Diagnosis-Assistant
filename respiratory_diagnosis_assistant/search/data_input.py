import csv
import pandas as pd
import os 
from pymongo import MongoClient

uri = "mongodb+srv://cs4440_8:cs4440_8@respiratory-diagnosis.hwlbmw8.mongodb.net/?retryWrites=true&w=majority&appName=respiratory-diagnosis"
# Create a new client and connect to the server
client = MongoClient(uri)
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e: 
    print(e)
    
###Diagnosis###

list = []
with open('respiratory_diagnosis_assistant\search\Respiratory_Sound_Database\Respiratory_Sound_Database\patient_diagnosis.csv', 'r') as file:
    data = csv.reader(file,delimiter = '\n')  # extracting one row 
    for i in data:
        list.append(i[0].split(';')) #splitting the data with delimiter ;
        
with open('updated_patient_diagnosis.csv', 'w',newline='') as data:
    writer = csv.writer(data)
    writer.writerows(list)

df = pd.read_csv("respiratory_diagnosis_assistant\search\Respiratory_Sound_Database\Respiratory_Sound_Database\patient_diagnosis.csv")  
data = df.to_dict("records")

db=client["respiratory-diagnosis"]
COLLECTION_NAME = "search_diagnosis"
collection = db[COLLECTION_NAME]

collection.insert_many(data)

###Patients###

df = pd.read_table("respiratory_diagnosis_assistant\search\Respiratory_Sound_Database\Respiratory_Sound_Database\demographic_info.txt", sep=' ', keep_default_na=False, na_values=None)  
data = df.to_dict("records")

COLLECTION_NAME = "search_patients"
collection = db[COLLECTION_NAME]

collection.insert_many(data)

###Respiratory Data###

files = os.listdir('respiratory_diagnosis_assistant\search\Respiratory_Sound_Database\Respiratory_Sound_Database\Audio_and_txt_files') 

data = []
for file in files:
    if(file.endswith(".txt")):
        patient_id, recording_index, chest_location, acquisition_model, recording_equipment = file.split('_')
        path = "respiratory_diagnosis_assistant\search\Respiratory_Sound_Database\Respiratory_Sound_Database\Audio_and_txt_files\\" + file
        df = pd.read_table(path, sep="\s+", header=None, 
                        names=["beginning_resp_cycle", "end_resp_cycle", "crackles", "wheezes"],
                        keep_default_na=False, na_values=None)  
        df = df.drop(columns=['crackles', 'wheezes'])
        resp_cycles = df.to_dict("records")

        data.append({'patient_id':patient_id, 
                                'recording_index':recording_index, 
                                'chest_location':chest_location, 
                                'acquisition_model':acquisition_model,
                                'recording_equipment':recording_equipment,
                                'annotation_file':file,
                                'respiratory_cycles':resp_cycles,
                                'sound_file_path':f'{file[:len(file)-4]}.wav'
                                })

COLLECTION_NAME = "search_respiratory_data"
collection = db[COLLECTION_NAME]

collection.insert_many(data)