from fastapi import FastAPI
from contextlib import asynccontextmanager
import utilidadesRedis
import utilidadesMongodb

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Inicializando con datos por defecto...") #   Parámetro iniciales de Redis
    utilidadesRedis.startup("allkeys-lru", "1024mb") #   Politica y tamaño
    yield
    print("Adios...")
app = FastAPI(lifespan=lifespan)

@app.get("/generalKenobi")  #   Health, si está arriba el contenedor
def generalKenobi():
    return {"Obi-Wan Kenobi": "Hello there!"}

@app.get("/redis/status")   #   Si está arriba redis
def redisStatus():
    return utilidadesRedis.redisPing()

@app.get("/mongodb/status") #   Si está arriba mongoDB
def mongodbStatus():
    return utilidadesMongodb.mongoPing()

@app.get("/cache/{alertType}/{UUID}")   #   Llamar a este endpoint como consulta a sistema
def cache(alertType: str, UUID: str):
    if utilidadesRedis.isInCache(UUID): #   Si está en cache retorna true (hit)
        return {"result": True}
    else:   #   Si no está en caché, lo agrega y retorna false (miss)
        value = utilidadesMongodb.getAlerta(alertType, UUID)
        utilidadesRedis.addKeyValue(UUID, value)
        return {"result": False}

@app.get("/changepolicy")  #   Intercambia politica de remoción entre lru y lfu
def changePolicy():
    return utilidadesRedis.changePolicy()

@app.get("/changesize/{size}")    #   size debe estar en mb
def changeSize(size: int):
    return utilidadesRedis.changeSize(f"{size}mb")