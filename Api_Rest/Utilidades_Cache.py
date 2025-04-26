import redis 
import json
from Configuraciones import Hosteo_Redis, Puerto_Redis#Datos_configuracion_redis  
r = redis.Redis(host=Hosteo_Redis, port = Puerto_Redis,decode_responses=True)#Cambiaresta wea

def Obtenerdatos_Cache(LLave):
    Valor = r.get(LLave)
    if Valor:
        return json.loads(Valor)
    else:
        print("No Existe el valor en caché")
        return None
    
def GuardarDatos_Cache(LLave, Datos, ttl : int = 10): # TTL = cambiar (Tiempo de vida)
    r.setex(LLave, ttl, json.dumps(Datos))