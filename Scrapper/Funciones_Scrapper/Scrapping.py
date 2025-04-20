import requests
import time
from datetime import datetime
from Funciones_Scrapper.Alertas_extrac import almacenar_alertas

def Scrapper(nombres, tops, bottoms, lefts, rights):
    Alertas_Totales = 0
    Trafico_Total = 0
    Alertas_json = []
    Jams_json = []
    for i in range(len(nombres)):   

        top, bottom, left, right = tops[i], bottoms[i], lefts[i], rights[i] #variables
        url= f"https://www.waze.com/live-map/api/georss?top={top}&bottom={bottom}&left={left}&right={right}&env=row&types=alerts,traffic"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200: # La solicitud enviada es correcta y los datos extraibles
                data = response.json()  
            Alertas_data = data.get("alerts", [])#recuperar json de las alertas
            Trafico_data = data.get("jams", [])#recuperar json de el trafico

            Alertas = len(data.get("alerts", [])) # Recuperar cantidad de alertas 
            Alertas_trafico = len(data.get("jams", [])) # Recuperar cantidad de alertas de trafico

            # Extraccion de los datos que necesitamos
            fecha_actual = datetime.now().isoformat() # Fecha actual

            for alerta in Alertas_data: # Extaccion de las alertas
                alerta["comuna"] = nombres[i] # Agregar la comuna a cada alerta
                alerta["fecha_subida"] = fecha_actual # Agregar la fecha de subida a cada alerta
                Alertas_json.append(alerta) # Agregar la alerta a la lista de alertas

            for trafico in Trafico_data:
                trafico["comuna"] = nombres[i]
                trafico["fecha_subida"] = fecha_actual
                Jams_json.append(trafico)

            print(f"Alertas totales en la Comuna: {nombres[i]} son {Alertas_trafico} y {Alertas}")
            Alertas_Totales += Alertas # Sumar las alertas de cada comuna
            Trafico_Total += Alertas_trafico # Sumar las alertas de trafico de cada comuna
        except:
            print(f"Error en recuperar datos en la comuna: {nombres[i]}")  
        time.sleep(2) #Para que no rechaze las peticiones el servidor
    almacenar_alertas(Alertas_json, "Alertas")
    almacenar_alertas(Jams_json, "Jams")
    print(f"Alertas totales son {Alertas_Totales}, las de trafico son {Trafico_Total} y todas juntas son {Alertas_Totales + Trafico_Total}")
    