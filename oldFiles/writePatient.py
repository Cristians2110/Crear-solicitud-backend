import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Función para conectar a la base de datos MongoDB
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

# Función para guardar el JSON en MongoDB
def save_patient_to_mongodb(patient_json_string, collection):
    """
    Guarda un documento JSON (representado como un string) en la colección de MongoDB.
    """
    try:
        # Convertir el JSON string a un diccionario de Python
        patient_data = json.loads(patient_json_string)

        # Insertar el documento en la colección de MongoDB
        result = collection.insert_one(patient_data)
        print(f"Documento insertado con ID: {result.inserted_id}")
        
        # Retornar el ID del documento insertado
        return result.inserted_id
    except json.JSONDecodeError as e:
        print(f"Error de formato JSON: {e}")
        return None
    except Exception as e:
        print(f"Error al guardar en MongoDB: {e}")
        return None

# Ejemplo de uso
if __name__ == "__main__":
    # Cadena de conexión a MongoDB (¡ACTUALIZAR CON TUS CREDENCIALES Y CLUSTER!)
    # Asegúrate de reemplazar <ALEX123> con tu contraseña real.
    uri = "mongodb+srv://christians210:ALEX123@cluster0.174y8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    # Nombre de la base de datos y la colección que quieres usar
    db_name = "RIS-FINAL"
    collection_name = "solicitud" # O la colección donde desees almacenar estos pacientes

    # Conectar a MongoDB
    collection = connect_to_mongodb(uri, db_name, collection_name)

    if collection:
        # JSON string correspondiente al artefacto Patient de HL7 FHIR
        # (Aunque el JSON no usa los 'system' de FHIR en los identificadores,
        # lo guardaremos tal cual como está definido en este string)
        patient_json = '''
        {
          "resourceType": "Patient",
          "identifier": [
            {
              "type": "cc",
              "value": "1020713756"
            },
            {
              "type": "pp",
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

        # Guardar el JSON en MongoDB
        inserted_id = save_patient_to_mongodb(patient_json, collection)

        if inserted_id:
            print(f"Paciente (JSON crudo) guardado exitosamente con ID: {inserted_id}")
        else:
            print("No se pudo guardar el paciente.")
    else:
        print("La conexión a la base de datos no se pudo establecer. No se intentará guardar el paciente.")