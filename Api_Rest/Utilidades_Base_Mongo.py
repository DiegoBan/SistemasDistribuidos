from pymongo import MongoClient
from Configuraciones import URL_Mongo, BASE_MONGO

cliente = MongoClient(URL_Mongo)
db = cliente[BASE_MONGO] 

def Get_Alerta_En_MongoDB(alerta_tipo: str, evento_id: str):
    # Seleccionar la colección según el tipo de alerta
    if alerta_tipo == "Alerta":
        coleccion_alertas = db["Alertas"]
    elif alerta_tipo == "Atasco":
        coleccion_alertas = db["Jams"]
    else:
        print(f"[Error] Tipo de alerta no válido: {alerta_tipo}") # Si la alerta no es valida 
        return None
    
    # Buscar por id
    return coleccion_alertas.find_one({"id": evento_id})
