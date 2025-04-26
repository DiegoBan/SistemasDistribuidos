from fastapi import FastAPI , HTTPException
from Utilidades_Cache import  Obtenerdatos_Cache , GuardarDatos_Cache
from Utilidades_Base_Mongo import Get_Alerta_En_MongoDB

app = FastAPI()

@app.get("/event/{tipo_evento}/{id_evento}")
def Obtener_Evento(tipo_evento: str, id_evento: str):
    if tipo_evento not in ["Alerta", "jam"]:
        raise HTTPException(status_code=400, detail="Tipo debe ser 'alert' o 'jam'")

    # Búsqueda en Redis
    llave_busqueda = f"{tipo_evento}:{id_evento}" # Creacion de la LLave de busqueda
    datos_obtenidos = Obtenerdatos_Cache(llave_busqueda) # Obtencion de datos

    if datos_obtenidos is not None: # Verificacion se encontro datos
        print("Datos encontrados en cache")
        return {"source": "cache", "data": datos_obtenidos} # Retorna datos encontrados
    else: # No se encontraron los datos en cache
        print("Datos no encontrados en Cache, buscando en Base de Datos")
        datos_obtenidos_mongo = Get_Alerta_En_MongoDB(tipo_evento, id_evento) # Busca en mongo
        if not datos_obtenidos_mongo: # No exiten los datos
            raise HTTPException(status_code=404, detail="Alerta no existente")
        else:
            GuardarDatos_Cache(llave_busqueda, datos_obtenidos_mongo)# Guardar datos en cache por si sale otra vez
            return {"source": "mongo", "data": datos_obtenidos_mongo} # Retorna los datos encontrados (para las estadisticas)

@app.get("/redis/{llave}") # Ver datos para verificar (Opcional)
def Ver_Dato_Redis(llave: str):

    dato = Obtenerdatos_Cache(llave)

    if dato is None:
        raise HTTPException(status_code=404, detail="Dato no encontrado en Redis")
    return {"llave": llave, "data": dato}

@app.get("/mongo/{tipo_evento}/{id_evento}")
def Ver_Dato_Mongo(tipo_evento: str, id_evento: str):

    dato = Get_Alerta_En_MongoDB(tipo_evento, id_evento)
    
    if not dato:
        raise HTTPException(status_code=404, detail="Dato no encontrado en MongoDB")
    return {"tipo_evento": tipo_evento, "id_evento": id_evento, "data": dato}