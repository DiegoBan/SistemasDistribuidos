import requests
import time
import numpy
import ramdom
from pymongo import MongoClient
from tqdm import tqdm
import matplotlib.pyplot

#Conexiones
URL_API = ""
client = MongoClient("mongo", 27017)
db = client["SD_db"]

#Variables
Consultas_Totales = 0 # Ingresar consults totales (tiene problemas desde terminar en docker)
Valor_promedio = 0.3 # Valor promedio de tiempo para los eventos 
Desviacion_Estandar = 0.1 # Para convertir a segundos mas accesibles 

#Buscar datos bases
UUID_Alertas = [Alertas["uuid"] for Alertas in db.Alertas.find({}, {"uuid": 1})]
UUID_Atasco = [Atascos["uuid"] for Atascos in db.Jams.find({}, {"uuid": 1})]

print(f"{len(UUID_Alertas)} Total de uuid de Alertas")
print(f"{len(UUID_Atasco)} Total de uuid de Atascos")

def Tiempo_Consultas():
    return numpy.random.normal(Valor_promedio,Desviacion_Estandar)

Aciertos = 0
Fallas = 0

# Consultas 

for i in range(Consultas_Totales):
    tipo = ramdom.choice(["Alerta","Atasco"])

    if tipo == "Alerta" :
        uuid = ramdom.choice(UUID_Alertas)
    elif tipo == "Atasco" :
        uuid = ramdom.choice(UUID_Atasco)
    else :
        print("ERROR EN EL TIPO")
    try:  
        URL = f"{URL_API}/cache/{tipo}/{uuid}"
        Respuesta = requests.get(URL)
        #Json_respuesta = Respuesta.get("") #indicar donde sale si fue cache o no
        if Respuesta == True :
            Aciertos += 1
        else :
            Fallas += 1
    except Exception as ERROR :
        print("ERROR EN LA CONSULTA", ERROR)
    
    time.sleep(Tiempo_Consultas())

Total = Aciertos + Fallas
Radio_Aciertos = (Aciertos/Total) * 100

print(f"Consultas Ejecutadas : {Total}")
print(f"Veces encontradas en cache: {Aciertos}")
print(f"Veces no encontradas en cache: {Fallas}")
print(f"Radio de aciertos en las consultas: {Radio_Aciertos}")

