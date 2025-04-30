import requests
import subprocess
from tabulate import tabulate

# Configuraciones a probar
policies = ['lru', 'lfu']
sizes = [128, 256] # potencias de 2: 128, 256, 512, 1024

# Guardar resultados
resultados = []

def cambiar_politica():
    res = requests.get("http://cache:8000/changepolicy")
    print(">> Política cambiada:", res.json())

def cambiar_tamano(size):
    res = requests.get(f"http://cache:8000/changesize/{size}")
    print(">> Tamaño cambiado:", res.json())

def ejecutar_test():
    proceso = subprocess.Popen(['python', 'Test_Trafico_Normal.py'], stdout=subprocess.PIPE, text=True)
    salida = proceso.communicate()[0]

    aciertos = int(extraer_valor(salida, "Veces encontradas en cache: "))
    fallas = int(extraer_valor(salida, "Veces no encontradas en cache: "))
    ratio = float(extraer_valor(salida, "Radio de aciertos en las consultas: ").replace("%", ""))
    
    return aciertos, fallas, ratio

def extraer_valor(texto, clave):
    for linea in texto.splitlines():
        if clave in linea:
            return linea.split(clave)[-1].strip()
    return None

# Ejecutar tests para cada combinación
for policy in policies:
    for size in sizes:
        print(f"\n===== Ejecutando prueba: Política={policy.upper()} | Tamaño={size}MB =====")
        
        cambiar_tamano(size)
        
        aciertos, fallas, ratio = ejecutar_test()
        
        resultados.append({
            "Política": policy.upper(),
            "Tamaño (MB)": size,
            "Aciertos": aciertos,
            "Fallas": fallas,
            "Efectividad (%)": round(ratio, 2)
        })
    cambiar_politica()

# Mostrar resultados en consola
print("\n==================== RESULTADOS FINALES ====================")
print(tabulate(resultados, headers="keys", tablefmt="fancy_grid"))
