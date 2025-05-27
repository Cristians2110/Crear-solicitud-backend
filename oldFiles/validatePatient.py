from pymongo import MongoClient
from pymongo.server_api import ServerApi
from fhir.resources.patient import Patient
import json

# --- Funciones de Conexión y Operaciones con MongoDB ---

def connect_to_mongodb(uri, db_name, collection_name):
    """
    Función para conectar a la base de datos MongoDB y obtener la colección.
    """
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        # PING para verificar la conexión
        client.admin.command('ping')
        print("Conexión a MongoDB exitosa!")
        db = client[db_name]
        collection = db[collection_name]
        return collection
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        return None

def insert_fhir_patient(collection, fhir_patient_resource):
    """
    Inserta un recurso FHIR Patient (como diccionario) en la colección de MongoDB.
    """
    try:
        # Los recursos FHIR son diccionarios, se pueden insertar directamente
        result = collection.insert_one(fhir_patient_resource.model_dump_json(by_alias=True, exclude_unset=True))
        print(f"Paciente FHIR insertado con ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        print(f"Error al insertar el paciente FHIR en MongoDB: {e}")
        return None

def find_fhir_patient_by_identifier(collection, identifier_type, identifier_value):
    """
    Busca un paciente FHIR en la colección por un identifier específico.
    Devuelve el documento de MongoDB (diccionario).
    """
    try:
        query = {
            "identifier": {
                "$elemMatch": {
                    "system": identifier_type,  # Usar 'system' en lugar de 'type' para FHIR
                    "value": identifier_value
                }
            }
        }
        patient_data = collection.find_one(query)
        return patient_data
    except Exception as e:
        print(f"Error al buscar paciente FHIR en MongoDB: {e}")
        return None

# --- Ejemplo de Uso ---

if __name__ == "__main__":
    # Configuración de conexión a MongoDB
    # ¡IMPORTANTE! Reemplaza <ALEX123> con tu contraseña real si no lo has hecho ya.
    MONGO_URI = "mongodb+srv://christians210:ALEX123@cluster0.174y8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    DB_NAME = "RIS-FINAL"
    COLLECTION_NAME = "solicitud" # O "patients" si prefieres una colección dedicada a pacientes FHIR

    # 1. Conectar a MongoDB
    collection = connect_to_mongodb(MONGO_URI, DB_NAME, COLLECTION_NAME)

    if collection:
        # 2. Definir el JSON del recurso Patient
        patient_json_string = '''
        {
          "resourceType": "Patient",
          "identifier": [
            {
              "system": "http://cedula",
              "value": "1020713756"
            },
            {
              "system": "http://pasaporte",
              "value": "AQ123456789"
            }
          ],
          "name": [
            {
              "use": "official",
              "text": "Mario Enrique Duarte",
              "family": "Duarte",
              "given": [
                "Mario",
                "Enrique"
              ]
            }
          ],
          "telecom": [
            {
              "system": "phone",
              "value": "3142279487",
              "use": "home"
            },
            {
              "system": "email",
              "value": "mardugo@gmail.com",
              "use": "home"
            }
          ],
          "gender": "male",
          "birthDate": "1986-02-25",
          "address": [
            {
              "use": "home",
              "line": [
                "Cra 55A # 167A - 30"
              ],
              "city": "Bogotá",
              "state": "Cundinamarca",
              "postalCode": "11156",
              "country": "Colombia"
            }
          ]
        }
        '''
        
        # 3. Validar y crear el objeto Patient FHIR desde el JSON
        try:
            # Parsear el JSON string a un diccionario Python
            patient_data_dict = json.loads(patient_json_string)
            # Validar el diccionario con el modelo Patient de fhir.resources
            fhir_patient = Patient.model_validate(patient_data_dict)
            print("\nObjeto Patient FHIR creado desde JSON:")
            print(fhir_patient.model_dump_json(indent=2)) # Imprime el objeto FHIR como JSON formateado
        except Exception as e:
            print(f"Error al validar el JSON de Patient: {e}")
            fhir_patient = None

        if fhir_patient:
            # 4. Insertar el objeto Patient FHIR en MongoDB
            # Usamos .model_dump() para obtener un diccionario Python que MongoDB puede almacenar.
            # `by_alias=True` asegura que los nombres de los campos sean los esperados por FHIR (ej: resourceType)
            # `exclude_unset=True` excluye campos que no se hayan establecido (para un JSON más limpio)
            insert_id = insert_fhir_patient(collection, fhir_patient)

            if insert_id:
                # 5. Buscar el paciente insertado en MongoDB usando un identificador
                print("\nBuscando el paciente recién insertado por Cédula:")
                found_patient_data = find_fhir_patient_by_identifier(collection, "http://cedula", "1020713756")

                if found_patient_data:
                    print("\nPaciente encontrado en MongoDB (datos crudos):")
                    print(json.dumps(found_patient_data, indent=2, default=str)) # default=str para ObjectId

                    # Opcional: Reconstruir el objeto Patient de fhir.resources desde los datos de MongoDB
                    try:
                        reconstructed_fhir_patient = Patient.model_validate(found_patient_data)
                        print("\nPaciente FHIR reconstruido desde MongoDB:")
                        print(reconstructed_fhir_patient.model_dump_json(indent=2))
                    except Exception as e:
                        print(f"Error al reconstruir el objeto Patient FHIR desde MongoDB: {e}")
                else:
                    print("No se encontró el paciente en MongoDB después de la inserción.")
            else:
                print("No se pudo insertar el paciente FHIR.")
    else:
        print("No se pudo establecer la conexión a la base de datos.")