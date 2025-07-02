import requests
import random
from elasticsearch import Elasticsearch

# Conexiones
URL_API = "http://localhost:8000" #cache
es = Elasticsearch("http://localhost:9200")  # elastic

# Total de consultas
Consultas_Totales = 15000

# Obtener UUIDs desde Elasticsearch
def obtener_uuids(indice, campo_uuid="uuid", limite=5500):
    resultado = es.search(
        index=indice,
        body={
            "_source": [campo_uuid],
            "query": { "match_all": {} },
            "size": limite
        }
    )
    return [hit["_source"][campo_uuid] for hit in resultado["hits"]["hits"]]

UUID_Alertas = obtener_uuids("alertas")
UUID_Atasco = obtener_uuids("jams")

print(f"{len(UUID_Alertas)} UUIDs de Alertas")
print(f"{len(UUID_Atasco)} UUIDs de Atascos")

# Métricas
Aciertos = 0
Fallas = 0

# Consultas
for _ in range(Consultas_Totales):
    tipo = random.choice(["Alertas", "Jams"])
    uuid = random.choice(UUID_Alertas if tipo == "Alertas" else UUID_Atasco)

    try:
        URL = f"{URL_API}/cache/{tipo}/{uuid}"
        Respuesta = requests.get(URL).json()

        if Respuesta["result"]:
            Aciertos += 1
        else:
            Fallas += 1
    except Exception as ERROR:
        print("ERROR EN LA CONSULTA", ERROR)

# Resultados
Total = Aciertos + Fallas
Radio_Aciertos = (Aciertos / Total) * 100

print(f"Consultas Ejecutadas : {Total}")
print(f"Encontradas en cache: {Aciertos}")
print(f"No encontradas en cache: {Fallas}")
print(f"Radio de aciertos: {Radio_Aciertos:.2f}%")