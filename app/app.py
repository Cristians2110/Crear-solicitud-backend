import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from fhir.resources.patient import Patient # Asegúrate de tener 'fhir.resources' instalado (pip install fhir.resources)

# --- Función para conectar a la base de datos MongoDB ---
def connect_to_mongodb(uri, db_name, collection_name):
    """
    Establece una conexión con MongoDB y devuelve el objeto de la colección.
    """
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        # Opcional: Haz un ping para confirmar la conexión
        client.admin.command('ping')
        print(f"Conexión exitosa a la base de datos '{db_name}' en MongoDB.")
        db = client[db_name]
        collection = db[collection_name]
        return collection
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None

# --- Configuración de conexión a MongoDB ---
# ¡IMPORTANTE! Reemplaza <ALEX123> con tu contraseña real de MongoDB Atlas.
MONGO_URI = "mongodb+srv://christians210:ALEX123@cluster0.174y8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "RIS-FINAL"
COLLECTION_NAME = "solicitud" # Tu colección para las solicitudes/pacientes

# Conectar a MongoDB al inicio del script
# La variable 'collection' estará disponible para todas las funciones.
collection = connect_to_mongodb(MONGO_URI, DB_NAME, COLLECTION_NAME)

# --- Funciones de Operaciones con Pacientes ---

def GetPatientById(patient_id: str):
    """
    Busca un paciente en la colección por su ID de MongoDB (_id).
    Convierte el ObjectId a string para la salida.
    """
    if collection is None:
        return "error: no_db_connection", None
    try:
        patient = collection.find_one({"_id": ObjectId(patient_id)})
        if patient:
            patient["_id"] = str(patient["_id"]) # Convertir ObjectId a string
            print(f"Paciente encontrado por ID: {patient_id}")
            return "success", patient
        print(f"Paciente con ID '{patient_id}' no encontrado.")
        return "notFound", None
    except Exception as e:
        print(f"Error al buscar paciente por ID '{patient_id}': {str(e)}")
        return f"error: {str(e)}", None

def WritePatient(patient_dict: dict):
    """
    Valida un diccionario como un recurso FHIR Patient y lo inserta en MongoDB.
    Retorna el estado y el ID insertado si es exitoso.
    """
    if collection is None:
        return "error: no_db_connection", None
    try:
        # Validar el diccionario con el modelo Patient de fhir.resources
        pat = Patient.model_validate(patient_dict)
    except Exception as e:
        print(f"Error de validación del paciente FHIR: {str(e)}")
        return f"errorValidating: {str(e)}", None
    
    # Convertir el objeto FHIR validado a un diccionario para insertar en MongoDB
    # by_alias=True para usar los nombres de campo FHIR (ej. resourceType)
    # exclude_unset=True para no incluir campos no establecidos
    validated_patient_data = pat.model_dump(by_alias=True, exclude_unset=True)
    
    try:
        result = collection.insert_one(validated_patient_data)
        if result.inserted_id: # Verificar si la inserción fue exitosa
            inserted_id = str(result.inserted_id)
            print(f"Paciente FHIR insertado con ID: {inserted_id}")
            return "success", inserted_id
        else:
            print("Error: No se obtuvo un ID después de la inserción.")
            return "errorInserting", None
    except Exception as e:
        print(f"Error al insertar el paciente en MongoDB: {str(e)}")
        return f"errorInserting: {str(e)}", None

def GetPatientByIdentifier(patientSystem: str, patientValue: str):
    """
    Busca un paciente en la colección por un identificador (system y value).
    Convierte el ObjectId a string para la salida.
    """
    if collection is None:
        return "error: no_db_connection", None
    try:
        # La consulta FHIR para identificadores usa 'system' y 'value'
        patient = collection.find_one({
            "identifier": {
                "$elemMatch": {
                    "system": patientSystem,
                    "value": patientValue
                }
            }
        })
        
        if patient:
            patient["_id"] = str(patient["_id"]) # Convertir ObjectId a string
            print(f"Paciente encontrado por identificador '{patientSystem}:{patientValue}'")
            return "success", patient
        print(f"Paciente con identificador '{patientSystem}:{patientValue}' no encontrado.")
        return "notFound", None
    except Exception as e:
        print(f"Error al buscar paciente por identificador: {str(e)}")
        return f"error: {str(e)}", None

# --- Ejemplo de Uso (Bloque principal) ---
if __name__ == "__main__":
    if collection is None:
        print("El script no puede continuar sin una conexión a la base de datos.")
    else:
        print("\n--- Demostración de funciones ---")

        # 1. Ejemplo de JSON de un paciente FHIR para insertar
        new_patient_data = {
            "resourceType": "Patient",
            "identifier": [
                {
                    "system": "http://cedula",
                    "value": "1234567890" # Nuevo valor para evitar duplicados si se ejecuta varias veces
                },
                {
                    "system": "http://pasaporte",
                    "value": "XYZ987654"
                }
            ],
            "name": [
                {
                    "use": "official",
                    "text": "Juan Perez",
                    "family": "Perez",
                    "given": ["Juan"]
                }
            ],
            "gender": "male",
            "birthDate": "1990-01-15"
        }

        # 2. Escribir/Insertar un nuevo paciente
        print("\nIntentando escribir un nuevo paciente...")
        status_write, patient_id_inserted = WritePatient(new_patient_data)
        print(f"Resultado de WritePatient: {status_write}, ID: {patient_id_inserted}")

        # 3. Obtener paciente por ID (si se insertó correctamente)
        if status_write == "success" and patient_id_inserted:
            print(f"\nIntentando obtener paciente por ID: {patient_id_inserted}...")
            status_get_by_id, found_patient_by_id = GetPatientById(patient_id_inserted)
            if status_get_by_id == "success":
                print("Paciente encontrado por ID:")
                print(json.dumps(found_patient_by_id, indent=2))
            else:
                print(f"No se pudo obtener el paciente por ID: {status_get_by_id}")

        # 4. Obtener paciente por identificador (usando el identificador del paciente que se intentó insertar)
        print("\nIntentando obtener paciente por identificador (Cédula: 1234567890)...")
        status_get_by_identifier, found_patient_by_identifier = GetPatientByIdentifier("http://cedula", "1234567890")
        if status_get_by_identifier == "success":
            print("Paciente encontrado por identificador:")
            print(json.dumps(found_patient_by_identifier, indent=2))
        else:
            print(f"No se pudo obtener el paciente por identificador: {status_get_by_identifier}")

        # 5. Ejemplo de búsqueda de un paciente que no existe
        print("\nIntentando obtener paciente por ID que no existe (ej. '60f8d1e0f8e4b5c7d8a9b0c1')...")
        status_not_found, _ = GetPatientById("60f8d1e0f8e4b5c7d8a9b0c1")
        print(f"Resultado: {status_not_found}")

        print("\n--- Fin de la demostración ---")