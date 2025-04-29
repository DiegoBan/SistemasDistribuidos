from fastapi import FastAPI, HTTPException
import utilidadesRedis
import utilidadesMongodb

app = FastAPI()
stats = {
    "hits": 0,
    "miss": 0
}

@app.get("/generalKenobi")
def generalKenobi():
    return {"Obi Wan Kenobi": "Hello there!"}

@app.get("/redis/status")
def redisStatus():
    return utilidadesRedis.redisPing()

@app.get("/mongodb/status")
def mongodbStatus():
    return utilidadesMongodb.mongoPing()

