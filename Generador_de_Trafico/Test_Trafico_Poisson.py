import requests
import time
import numpy
import random
from pymongo import MongoClient
from tqdm import tqdm
import matplotlib.pyplot

#Conexiones
URL_API = "http://cache:8000"
client = MongoClient("mongo", 27017)
db = client["SD_db"]

#Variables
Consultas_Totales = 20000 # Ingresar consults totales (tiene problemas desde terminar en docker)
LAMBDA = 1.5 # Distribucion media para los eventos 
Escala_Segundos = 10 # Para convertir a segundos mas accesibles 

#Buscar datos bases
UUID_Alertas = [Alertas["uuid"] for Alertas in db.Alertas.find({}, {"uuid": 1}).limit(10000)]
UUID_Atasco = [Atascos["uuid"] for Atascos in db.Jams.find({}, {"uuid": 1}).limit(10000)]

print(f"{len(UUID_Alertas)} Total de uuid de Alertas")
print(f"{len(UUID_Atasco)} Total de uuid de Atascos")

def Tiempo_Consultas():
    t = numpy.random.poisson(LAMBDA)/Escala_Segundos
    if t < 0:
        return -t
    else:
        return t

Aciertos = 0
Fallas = 0

# Consultas 

for i in range(Consultas_Totales):
    tipo = random.choice(["Alertas","Jams"])

    if tipo == "Alertas" :
        uuid = random.choice(UUID_Alertas)
    elif tipo == "Jams" :
        uuid = random.choice(UUID_Atasco)
    else :
        print("ERROR EN EL TIPO")
    try:  
        URL = f"{URL_API}/cache/{tipo}/{uuid}"
        Respuesta = requests.get(URL).json()
        #Json_respuesta = Respuesta.get("") #indicar donde sale si fue cache o no
        if Respuesta["result"]:
            Aciertos += 1
            print(f"encontrado en cache: {uuid}")
        else :
            Fallas += 1
            print(f"no encontrado en cache: {uuid}")
    except Exception as ERROR :
        print("ERROR EN LA CONSULTA", ERROR)
    
    time.sleep(Tiempo_Consultas())

Total = Aciertos + Fallas
Radio_Aciertos = (Aciertos/Total) * 100

print(f"Consultas Ejecutadas : {Total}")
print(f"Veces encontradas en cache: {Aciertos}")
print(f"Veces no encontradas en cache: {Fallas}")
print(f"Radio de aciertos en las consultas: {Radio_Aciertos}%")

