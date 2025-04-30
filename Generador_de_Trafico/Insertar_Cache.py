import requests
import time
import numpy
import random
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

#Conexiones
URL_API = ""
client = MongoClient("mongo", 27017)
db = client["SD_db"]
collection_Alertas = db["Alertas"]
collection_Jams = db["Jams"]
#Buscar datos bases
UUID_Alertas = [Alertas["uuid"] for Alertas in db.Alertas.find({}, {"uuid": 1})]
UUID_Atasco = [Atascos["uuid"] for Atascos in db.Jams.find({}, {"uuid": 1})]
Datos_Totales = 1000

for i in range(Datos_Totales):

    uuid_Alertas = random.choice(UUID_Alertas)
    uuid_Atasco = random.choice(UUID_Atasco)
    
    url_Alertas = f"{URL_API}/cache/Alertas/{uuid_Alertas}"
    response_Alertas = requests.get(url_Alertas)

    if response_Alertas.status_code == 200:
        print("Datos Enviados Exitosamente")
    else:
        print("Los datos no fueron enviados:", response_Alertas.status_code, response_Alertas.text)

    url_Atascos = f"{URL_API}/cache/Jams/{uuid_Atasco}"
    response_Atascos = requests.get(url_Atascos)
    if response_Atascos.status_code == 200:
        print("Datos Enviados Exitosamente")
    else:
        print("Los datos no fueron enviados:", response_Atascos.status_code, response_Atascos.text)

        

