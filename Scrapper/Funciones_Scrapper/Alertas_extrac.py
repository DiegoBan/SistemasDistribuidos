import requests 
import time
import csv

def almacenar_alertas(alertas,nombre_archivo):
    if alertas:
        keys = alertas[0].keys()
        with open(nombre_archivo, "w", newline="", encoding="utf-8") as archivo_csv:
            writer = csv.DictWriter(archivo_csv, fieldnames=keys)
            writer.writeheader()
            writer.writerows(alertas)
        print(f"📁 Se guardaron {len(alertas)} alertas en {nombre_archivo}")
    else:
        print(f"⚠️ No hay alertas para guardar en {nombre_archivo}.")