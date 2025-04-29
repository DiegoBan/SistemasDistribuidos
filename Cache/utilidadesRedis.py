import redis
import json

redisClient = redis.Redis(host = "redis", port = 6379, db = 0, decode_responses=True)

def redisPing():
    try:
        if redisClient.ping():
            return {"Redis": "Conexión establecida"}
    except redis.ConnectionError as e:
        return {"Redis": "No hay conexión", "error": str(e)}

def ObtenerLlave(key):
    value = redisClient.get(key)
    if(value):
        return json.loads(value)
    else:
        print(f"Valor de llave {key} no presente en cache")
        return None

def addKeyValue(key, value, TTL : int):
    redisClient.setex(key, TTL, json.dumps(value))