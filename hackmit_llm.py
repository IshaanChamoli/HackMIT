import requests
import json
from datetime import datetime, date
import copy
import csv
import pandas as pd

TODAY = datetime.today()

with open('/Users/umangbansal/Desktop/patients_data3.json', 'r') as file:
    data = json.load(file)

encounters = set()
medications = set()
relation_dict = {}
exclude = ".,?!\n\""
relation_without_weights = {}

for line in range(len(data)):
    for surgery in data[line]["medicalHistory"]["surgeries"]:
        encounters.add(surgery["type"])
    for hosp in data[line]["medicalHistory"]["pastHospitalizations"]:
        encounters.add(hosp["reason"])
    for visit in data[line]["visitRecords"]:
        encounters.add(visit["reason"])
    for meds in data[line]["currentMedications"]:
        medications.add(meds["medicationName"])

MODEL_ID = "8w6yyp2q"
BASETEN_API_KEY = "YMKFudUr.FcjOTi13DlaR3ZtCbBIumoXeqFJy25yx" # Paste from Discord
for med in medications:
    relation_dict[med] = {}
    relation_without_weights[med] = {}
    for reason in encounters:
        messages = [
            {"role": "system", "content": "You are a doctor determining what medications to prescribe a patient after a doctor's visit"},
            {"role": "user", "content": "Is it common to prescribe"+med+" after"+reason+"? Please answer with a yes or no"},
        ]
        payload = {
            "messages": messages,
            "stream": False,
            "max_tokens": 2048,
            "temperature": 0.9
        }
        # Call model endpoint
        res = requests.post(
            f"https://model-{MODEL_ID}.api.baseten.co/production/predict",
            headers={"Authorization": f"Api-Key {BASETEN_API_KEY}"},
            json=payload,
            stream=True
        )
        # Print the generated tokens as they get streamed
        # for content in res.iter_content():
        #     print(content.decode("utf-8"), end="", flush=True)
            # resp = ''.join(ch for ch in resp if ch not in exclude)
            # print(resp)
        resp = res.text
        resp = ''.join(ch for ch in resp if ch not in exclude)
        
        if (resp == "Yes"):
            messages = [
                {"role": "system", "content": "You are a doctor determining what medications to prescribe a patient after a doctor's visit"},
                {"role": "user", "content": "How many days is "+med+" commonly prescribed after"+reason+"? Please answer only with a positive number"},
            ]
            payload = {
                "messages": messages,
                "stream": False,
                "max_tokens": 2048,
                "temperature": 0.9
            }
            # Call model endpoint
            res = requests.post(
                f"https://model-{MODEL_ID}.api.baseten.co/production/predict",
                headers={"Authorization": f"Api-Key {BASETEN_API_KEY}"},
                json=payload,
                stream=True
            )

            weight = res.text
            weight = ''.join(ch for ch in weight if ch not in exclude)
            relation_dict[med][reason] = int(weight)
            relation_without_weights[med][reason] = 1
        else: 
            relation_dict[med][reason] = 0

print(relation_without_weights)

updated_history = {}
full_set = []
for line in data:
    id = line["patientID"]
    current_meds = line["currentMedications"]
    surgeries = line["medicalHistory"]["surgeries"]
    hosps = line["medicalHistory"]["pastHospitalizations"]
    visits = line["visitRecords"]
    if (id in updated_history.keys()):
        new_date = datetime(1, 1, 1)
        for enc in surgeries+hosps+visits:
            day = datetime.strptime(enc["date"], '%Y-%m-%d')
            if (day > new_date):
                new_date = day
        old_date = datetime(1, 1, 1)
        old_surg = updated_history[id]["medicalHistory"]["surgeries"]
        old_hosps = updated_history[id]["medicalHistory"]["pastHospitalizations"]
        old_visits = updated_history[id]["visitRecords"]  
        for enc in old_surg+old_hosps+old_visits:
            day = datetime.strptime(enc["date"], '%Y-%m-%d')
            if (day > old_date):
                old_date = day
        if (new_date > old_date):
            updated_history[id]["name"] = line["name"]
            updated_history[id]["dateOfBirth"] = line["dateOfBirth"]
            updated_history[id]["gender"] = line["gender"]
            updated_history[id]["contactInformation"] = line["contactInformation"]
            updated_history[id]["emergencyContact"] = line["emergencyContact"]
            updated_history[id]["currentMedications"] = line["currentMedications"]
            updated_history[id]["insuranceDetails"] = line["insuranceDetails"]
            updated_history[id]["primaryPhysician"] = line["primaryPhysician"]
        for allergy in line["medicalHistory"]["allergies"]:
            if (allergy not in updated_history[id]["medicalHistory"]["allergies"]):
                updated_history[id]["medicalHistory"]["allergies"].append(allergy)
        for cond in line["medicalHistory"]["chronicConditions"]:
            if (cond not in updated_history[id]["medicalHistory"]["chronicConditions"]):
                updated_history[id]["medicalHistory"]["chronicConditions"].append(cond)
        for surgery in line["medicalHistory"]["surgeries"]:
            if (surgery not in updated_history[id]["medicalHistory"]["surgeries"]):
                updated_history[id]["medicalHistory"]["surgeries"].append(surgery)
        for fatherCond in line["medicalHistory"]["familyMedicalHistory"]["father"]:
            if (fatherCond not in updated_history[id]["medicalHistory"]["familyMedicalHistory"]["father"]):
                updated_history[id]["medicalHistory"]["familyMedicalHistory"]["father"].append(fatherCond)
        for motherCond in line["medicalHistory"]["familyMedicalHistory"]["mother"]:
            if (motherCond not in updated_history[id]["medicalHistory"]["familyMedicalHistory"]["mother"]):
                updated_history[id]["medicalHistory"]["familyMedicalHistory"]["mother"].append(motherCond)
        for hospital in line["medicalHistory"]["pastHospitalizations"]:
            if (hospital not in updated_history[id]["medicalHistory"]["pastHospitalizations"]):
                updated_history[id]["medicalHistory"]["pastHospitalizations"].append(hospital)
        for record in line["visitRecords"]:
            if (record not in updated_history[id]["visitRecords"]):
                updated_history[id]["visitRecords"].append(record)
        for lab in line["laboratoryResults"]:
            if (lab not in updated_history[id]["laboratoryResults"]):
                updated_history[id]["laboratoryResults"].append(lab)
        for med in line["currentMedications"]:
            if (med not in updated_history[id]["currentMedications"]):
                updated_history[id]["currentMedications"].append(med)
    else:
        updated_history[id] = copy.deepcopy(line)

for id in updated_history.keys():
    meds = copy.deepcopy(updated_history[id]["currentMedications"])
    updated_history[id]["currentMedications"] = []
    for med in meds:
        count = 0
        for surg in updated_history[id]["medicalHistory"]["surgeries"]:
            date = datetime.strptime(surg["date"], '%Y-%m-%d')
            duration = (TODAY - date).total_seconds()
            if (duration < relation_dict[med["medicationName"]][surg["type"]]*24*3600):
                count = count + 1
        for hosp in updated_history[id]["medicalHistory"]["pastHospitalizations"]:
            date = datetime.strptime(hosp["date"], '%Y-%m-%d')
            duration = (TODAY - date).total_seconds()
            if (duration < relation_dict[med["medicationName"]][hosp["reason"]]*24*3600):
                count = count + 1
        for visit in updated_history[id]["visitRecords"]:
            date = datetime.strptime(visit["date"], '%Y-%m-%d')
            duration = (TODAY - date).total_seconds()
            if (duration < relation_dict[med["medicationName"]][visit["reason"]]*24*3600):
                count = count + 1
        if (count > 1):
            updated_history[id]["currentMedications"].append(copy.deepcopy(med))
    full_set.append(updated_history[id])

sparse_set = []
for id in updated_history.keys():
    patient_dict = {}
    patient_dict["id"] = int(id[18:])
    patient_dict["name"] = updated_history[id]["name"]["first"] + " " + updated_history[id]["name"]["middle"] + " " + updated_history[id]["name"]["last"]
    patient_dict["allergies"] = ' '.join(ch for ch in updated_history[id]["medicalHistory"]["allergies"])
    patient_dict["chronicConditions"] = ' '.join(ch for ch in updated_history[id]["medicalHistory"]["chronicConditions"])
    patient_dict["surgeries"] = ' '.join(ch["type"] for ch in updated_history[id]["medicalHistory"]["surgeries"])
    patient_dict["currentMedications"] = ' '.join(ch["medicationName"]+", "+ch["dosage"]+", "+ch["frequency"] for ch in updated_history[id]["currentMedications"])
    patient_dict["allDetails"] = str(updated_history[id])
    sparse_set.append(patient_dict)

df = pd.DataFrame(data={"col1": sparse_set})
df.to_csv("/Users/umangbansal/Desktop/patient_records.csv", sep=',',index=False)

# print(sparse_set[0:5])

with open("/Users/umangbansal/Desktop/patient_records.json", "w") as outfile: 
    json.dump(full_set, outfile)