from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Función para conectar a la base de datos MongoDB
def connect_to_mongodb(uri, db_name, collection_name):
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client[db_name]
    collection = db[collection_name]
    return collection

# Función para buscar pacientes por un identifier específico
def find_patient_by_identifier(collection, identifier_type, identifier_value):
    try:
        # Consultar el documento que coincida con el identifier
        query = {
            "identifier": {
                "$elemMatch": {
                    "type": identifier_type,
                    "value": identifier_value
                }
            }
        }
        patient = collection.find_one(query)
        
        # Retornar el paciente encontrado
        return patient
    except Exception as e:
        print(f"Error al buscar en MongoDB: {e}")
        return None

# Función para mostrar los datos de un paciente
def display_patient(patient):
    if patient:
        print("Paciente encontrado:")
        print(f"  ID: {patient.get('_id')}")
        # Asegúrate de que las claves 'name', 'given', 'family' existan antes de acceder a ellas
        patient_name = patient.get('name', [{}])[0]
        given_name = patient_name.get('given', [''])[0]
        family_name = patient_name.get('family', '')
        print(f"  Nombre: {given_name} {family_name}")
        print(f"  Género: {patient.get('gender', 'Desconocido')}")
        print(f"  Fecha de nacimiento: {patient.get('birthDate', 'Desconocida')}")
        print("  Identificadores:")
        for identifier in patient.get("identifier", []):
            print(f"    Type: {identifier.get('type')}, Valor: {identifier.get('value')}")
    else:
        print("No se encontró ningún paciente con el identifier especificado.")

# Ejemplo de uso
if __name__ == "__main__":
    # Cadena de conexión a MongoDB (reemplaza con tu propia cadena de conexión)
    # ¡IMPORTANTE! Reemplaza <ALEX123> con tu contraseña real si no lo has hecho ya.
    uri = "mongodb+srv://christians210:ALEX123@cluster0.174y8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    # Nombre de la base de datos y la colección que me proporcionaste
    db_name = "RIS-FINAL"
    collection_name = "solicitud"

    # Conectar a MongoDB
    collection = connect_to_mongodb(uri, db_name, collection_name)
    
    # Identifier específico a buscar (puedes ajustar estos valores según lo que busques en tu colección 'solicitud')
    # Dado que la colección es 'solicitud', es probable que los identificadores de paciente estén anidados de otra forma.
    # Necesitaríamos saber la estructura de un documento en tu colección 'solicitud' para una consulta precisa.
    # Por ejemplo, si en 'solicitud' tienes un campo 'paciente.identificador.cc', la consulta sería diferente.
    # Mantendré la estructura original por ahora, asumiendo que 'solicitud' también tiene una estructura similar a 'patients'.
    identifier_type = "cc" # Tipo de identificador (ej: "cc" para cédula de ciudadanía)
    identifier_value = "1020713756" # Valor del identificador

    # Buscar el paciente por identifier
    patient = find_patient_by_identifier(collection, identifier_type, identifier_value)
    
    # Mostrar los datos del paciente encontrado
    display_patient(patient)