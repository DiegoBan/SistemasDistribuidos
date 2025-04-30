import redis
import json

redisClient = redis.Redis(host = "redis", port = 6379, db = 0, decode_responses=True)

def redisPing():
    try:
        if redisClient.ping():
            return {"Redis": "Conexión establecida"}
    except redis.ConnectionError as e:
        return {"Redis": "No hay conexión", "error": str(e)}

def startup(policy: str, size: str):
    try:
        redisClient.config_set("maxmemory", size)
        redisClient.config_set("maxmemory-policy", policy)
    except redis.ConnectionError as e:
        print(f"Redis error: {e}")

def ObtenerLlave(key):
    try:
        value = redisClient.get(key)
        if(value):
            return json.loads(value)
        else:
            print(f"Valor de llave {key} no presente en cache")
            return None
    except redis.ConnectionError as e:
        return {"Error en Redis": str(e)}

def addKeyValue(key: str, value: str):
    try:
        redisClient.setex(key, 5000, json.dumps(value))
    except redis.ConnectionError as e:
        return {"Error en Redis": str(e)}

def isInCache(key): #   Verifica si una llave está en cache o no
    try:
        return redisClient.exists(key)
    except redis.ConnectionError as e:
        return {"Error en Redis": str(e)}
    
def changeSize(size: str):
    try:
        redisClient.config_set("maxmemory", size)
        return {"CacheSizeChangedTo": size}
    except redis.ConnectionError as e:
        return {"Redis error": e}

def changePolicy():
    policy = redisClient.config_get("maxmemory-policy")
    if policy["maxmemory-policy"] == "allkeys-lru":
        redisClient.config_set("maxmemory-policy", "allkeys-lfu")
        return {"changedTo": "lfu"}
    else:
        redisClient.config_set("maxmemory-policy", "allkeys-lru")
        return {"changedTo": "lru"}