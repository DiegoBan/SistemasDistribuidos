import requests
import time
import numpy
import ramdom
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

#Conexiones
URL_API = ""
client = MongoClient("mongo", 27017)
db = client["SD_db"]
collection_Alertas = db["Alertas"]
collection_Jams = db["Jams"]
#Buscar datos bases
UUID_Alertas = [Alertas["uuid"] for Alertas in db.Alerta.find({}, {"uuid": 1})]
UUID_Atasco = [Atascos["uuid"] for Atascos in db.Atasco.find({}, {"uuid": 1})]
Datos_Totales = 1000
for i in range(Datos_Totales):

        uuid_Alertas = ramdom.choice(UUID_Alertas)
        uuid_Atasco = ramdom.choice(UUID_Atasco)

        if isInCache(uuid_Alertas) == True :
                print(f"Datos con ID: {uuid_Alertas} ya existe")
        else :
               Datos = collection_Alertas.find_one({"uuid": uuid_Alertas})
               addKeyValue(uuid_Alertas, Datos)

        if isInCache(uuid_Atasco) == True :
                print(f"Datos con ID: {uuid_Atasco} ya existe")
        else :
               Datos_Jams = collection_Jams.find_one({"uuid": uuid_Atasco})
               addKeyValue(uuid_Atasco, Datos)

