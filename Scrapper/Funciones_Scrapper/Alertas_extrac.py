from pymongo import MongoClient

def almacenar_alertas(data, dataType):
    if len(data) > 0:
        try:
            client = MongoClient("mongo", 27017)
            db = client["SD_db"]
            coleccion = db[dataType]
            respuesta = coleccion.insert_many(data)
            if len(respuesta.inserted_ids) > 0:
                print(f"Se insertaron correctamente {len(respuesta.inserted_ids)} del tipo {dataType}")
        except:
            print("Error al insertar los datos en la base de datos")
    else:
        print(f"No hay data del tipo {dataType}")