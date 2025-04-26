import redis 
import json
from Configuraciones import #Datos_configuracion_redis  
r = redis.Redis(host='localhost', port=6379, db=0)#Cambiaresta wea

def Obtenerdatos_Cache(LLave):
    Valor = r.get(LLave)
    if Valor:
        return json.loads(Valor)
    else:
        print("No Existe el valor en caché")
        return None
    
def GuardarDatos_Cache(LLave, Datos, ttl : int = 10): # TTL = cambiar (Tiempo de vida)
    r.setex(LLave, ttl, json.dumps(Datos))