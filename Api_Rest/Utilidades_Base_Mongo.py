from pymongo import MongoClient
from bson import ObjectId

cliente = MongoClient("mongodb://localhost:27017/")
db = cliente[]#Nombre de la base de datos]

def Get_Alerta_En_MongoDB(Alerta_Tipo : str, Evento_id):
    if Alerta_Tipo == "Alerta":
        colleccion_Alertas = db["Alerts"]
    elif Alerta_Tipo == "Atasco":
        colleccion_Alertas = db["jams"]
    else:
        print("Tipo de alerta no válido")
        return None
    
    return colleccion_Alertas.find_one({"id": Evento_id})