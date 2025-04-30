from fastapi import FastAPI, HTTPException
import utilidadesRedis
import utilidadesMongodb

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Inicializando con datos por defecto...") #   Parámetro iniciales de Redis
    utilidadesRedis.startup("allkeys-lru", "100mb") #   Politica y tamaño
    yield
    print("Adios...")
app = FastAPI()

@app.get("/generalKenobi")  #   Health, si está arriba el contenedor
def generalKenobi():
    return {"Obi Wan Kenobi": "Hello there!"}

@app.get("/redis/status")   #   Si está arriba redis
def redisStatus():
    return utilidadesRedis.redisPing()

@app.get("/mongodb/status") #   Si está arriba mongoDB
def mongodbStatus():
    return utilidadesMongodb.mongoPing()

@app.get("/cache/{alertType}/{UUID}")
def cache(alertType: str, UUID: str):
    if utilidadesRedis.isInCache(UUID):
        return True
    else:
        value = utilidadesMongodb.getAlerta(alertType, UUID)
        utilidadesRedis.addKeyValue(UUID, value)

@app.get("cache/changepolicy")  #   Intercambia politica de remoción entre lru y lfu
def changePolicy():
    return utilidadesRedis.changePolicy()

@app.get("/cache/changeSize/{size}")    #   size debe estar en mb
def changeSize(size: int):
    return utilidadesRedis.changeSize("{size}mb")