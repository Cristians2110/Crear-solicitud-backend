from fastapi import FastAPI, HTTPException
from fhir.resources.patient import Patient
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import os

app = FastAPI()

# MongoDB Atlas URL (Render guarda esto como variable de entorno)
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client["RIS-FINAL"]
collection = db["solicitud"]

def convert_id(patient):
    patient["_id"] = str(patient["_id"])
    return patient

@app.post("/patient")
def create_patient(patient_data: dict):
    try:
        pat = Patient.model_validate(patient_data)
        data = pat.model_dump(by_alias=True, exclude_unset=True)
        result = collection.insert_one(data)
        return {"inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patient/id/{patient_id}")
def get_patient_by_id(patient_id: str):
    try:
        patient = collection.find_one({"_id": ObjectId(patient_id)})
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return convert_id(patient)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/patient/identifier")
def get_patient_by_identifier(system: str, value: str):
    try:
        patient = collection.find_one({
            "identifier": {
                "$elemMatch": {
                    "system": system,
                    "value": value
                }
            }
        })
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return convert_id(patient)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
