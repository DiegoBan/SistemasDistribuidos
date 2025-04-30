from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

client = MongoClient("mongo", 27017)
db = client["SD_db"]

def mongoPing():
    try:
        client.admin.command('ping')
        return {"MongoDB": "Conexión establecida"}
    except ConnectionFailure as e:
        return {"MongoDB": "No hay conexión", "error": str(e)}
    
def getAlerta(alertType: str, eventUUID: str):
    if alertType == "Alerta":
        collection = db["Alertas"]
    elif alertType == "Atasco":
        collection = db["Jams"]
    else:
        print(f"[Error] Tipo de alerta no válido: {alertType}")
        return None
    
    return collection.find_one({"uuid": eventUUID})