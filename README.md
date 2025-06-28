#   Tareas Sistemas Distribuidos

Repositorio para tareas Sistemas Distribuidos.

Profesor: Nicolás Hidalgo.

Alumnos: Diego Banda, Dante Hortuvia.

Ayudantes: César Muñoz, Joaquín Villegas.

### Uso de Docker

Se utiliza docker, a través de dockerfiles y docker-compose para separar los distintos componentes de la/las tareas en contenedores.
Para inicializar los distintos contenedores y levantar el entorno, se utiliza lo siguiente en la carpeta raíz del proyecto:

```bash
docker-compose up --build -d
```

Para terminar la ejecución del entorno se utiliza:

```bash
docker-compose down
```

En caso de querer eliminar todos los contenedores detenidos se puede utilizar:

```bash
docker container prune
```

Asegurate de tener instalado Docker y Docker Compose antes de iniciar el proyecto.

## Entrega 1

###  Scrapper

El scrapper obtiene información desde la página de [Waze](https://www.waze.com/es-419/live-map/), obteniendo desde cada comuna de la región metropolitana sus alertas y tráfico del momento, para posteriormente guardarlo en el Almacenamiento.
Al inicializar el entorno de docker-compose, automaticamente se realiza una ejecuión del Scrapper, añadiendo más datos a la base de datos, sin embargo, si el entorno ya está levantado y se desea realizar otra ejecución, se debe entrar a la consola del contenedor a través de:

```bash
docker exec -it Scrapper bash
```

Y ejecutar:

```bash
python Web_Scrapper.py
```

###  Almacenamiento

Para el almacenamiento se utilizó la base de datos noSQL mongoDB, a través de su imagen oficial de Docker, abriendola en el puerto "27017" y creando un volumen (para el guardado de datos local) en la carpeta "./Almacenamiento:/data/db".
Para conectarse con la consola de mongodb se puede utilizar el comando:

```bash
docker exec -it distribuidos_db mongosh
```

Para contar cuantos datos hay en una colección, se puede utilizar lo siguiente (dentro de la consola de mongo):

```bash
db.collection.countDocuments({})
```

###  Generador de Tráfico

El trafico se genera a través de un script de python, el cual utilizando una distribución (Normal o Poisson) genera una cantidad de tráfico cada x tiempo determinado antes de iniciar, envía el tráfico y recibe una resuesta en forma de True o False que significa si estába en caché o no.
Estos scripts se ejecutan entrando al contendor que tiene estos scripts:

```bash
docker exec -it generador_de_trafico bash
```

Una vez en la consola del contenedor que tiene los scripts de python, se debe ejecutar alguno de los dos generadores de tráfico con:

```bash
python Test_Trafico_Normal.py
```
```bash
python Test_Trafico_Poisson.py
```

###  Sistema de Cache

Utilizando Redis, se crea una memoria cache (en memoria principal), el cual puede tener distintos tamaños o política de remoción.
El tamaño de este se puede intercambiar a través de http://0.0.0.0:8000/changesize/{size} (o desde contenedores: http://cache:8000/changesize/{size}), en el cual size es un número que representa el tamaño de la memoria para cache en MB.
Por otro lado tenemos la política de remoción, las cuales son LRU (Last Recently Use) o LFU (Least Frecuently Use), estas se intercambian entre sí tan solo llamando a http://0.0.0.0:8000/changepolicy (o desde contenedores: http://cache:8000/changepolicy).

## Entrega 2

### Filtering y Homogeneización

Se utiliza un script de pig para realizar la eliminación de duplicados, filtrado y homogenización de los datos obtenidos a través del scrapping, para realizar este proceso, primero se deben obtener los datos desde la base de datos mongoDB en un csv que utilizará posteriormente pig, para ello se deben insertar los siguientes comandos:

1. Obtención de Alertas:
```bash
docker exec -it distribuidos_db mongoexport \
  --host localhost \
  --db SD_db \
  --collection Alertas \
  --type=csv \
  --fields uuid,country,city,street,type,subtype,location.x,location.y,pubMillis,fecha_subida \
  --out /datos/alertas.csv
```
2. Obtención de Jams (Atascos):
```bash
docker exec -it distribuidos_db mongoexport \
  --host localhost \
  --db SD_db \
  --collection Jams \
  --type=csv \
  --fields uuid,severity,country,length,speed,city,street,type,line.0.x,line.0.y,pubMillis,fecha_subida \
  --out /datos/jams.csv
```

Después de ejecutar lo anterior, tendrémos dos csv en nuestra carpeta local, los cuales se deben mover al contenedor de hadoop para hacer el filtrado con pig.

1. Primero se copian a la carpeta del contenedor de hadoop:
```bash
docker cp ./data_host/alertas.csv distribuidos_hadoop:/alertas.csv
docker cp ./data_host/jams.csv distribuidos_hadoop:/jams.csv
```
3. Con los pasos anteriores tedrémos los datos en la carpeta del contenedor, sin embarno no dentro de este mismo, para ello primero entramos en el entorno de hadoop:
```bash
docker exec -it distribuidos_hadoop bash
```
4. Para luego mover los datos dentro de la carpeta deseada:
```bash
hdfs dfs -mkdir -p /datos
hdfs dfs -copyFromLocal -f /alertas.csv /datos/alertas.csv
hdfs dfs -copyFromLocal -f /jams.csv /datos/jams.csv
exit
```

Una vez se ejecutó lo anterior, está listo el entorno en hadoop para poder ejecutar el script de pig desde su propio contenedor y que este se conecte correctamente a hadoop para realizar el filtrado a través de :

1. Conectarse a contenedor con pig:
```bash
docker exec -it distribuidos_pig bash
```
2. Ejecutar eliminado y filtrado de datos:
```bash
pig Eliminacion_duplicados_y_filtrado.pig
```
Ten en cuenta que si ya has ejecutado el scipt antes, deberás eliminar las carpetas con los resultados antes, ya que pig no sobreescribe:
```bash
hdfs dfs -rm -r /datos/*_output
```

Finalizando esto, ya puedes salir del contenedor:
```bash
exit
```

En caso de querer obtener los resultados obtenidos por este script, deberás obtenerlos a través de:

1. Entrar a contenedor de hadoop:
```bash
docker exec -it distribuidos_hadoop bash
```

2. Extraer los archivos:
```bash
hdfs dfs -get /datos/alertas_output/part-r-00000 /alertas_resultado.csv
hdfs dfs -get /datos/jams_output/part-r-00000 /jams_resultado.csv
exit
```

3. Moverlos a la carpeta local para una visualización más cómoda en tu máquina.
```bash
docker cp distribuidos_hadoop:/alertas_resultado.csv ./data_host/alertas_resultado.csv
docker cp distribuidos_hadoop:/jams_resultado.csv ./data_host/jams_resultado.csv
```

### Processing

Una vez ejecutamos el eliminado de duplicados, filtrado y homogenización (Independiente de si se extrajo la información a local o no), se puede realizar un análisis de esta información obtenida, esto a través de un script de pig, para ejecutarlo debemos entrar al contenedor de pig y ejecutar el código.

1. Conectarse a contenedor de pig:
```bash
docker exec -it distribuidos_pig bash
```

2. Ejecutar procesamiento:
```bash
pig Procesado_datos.pig
```

Debes tener en cuenta que si ya ejecutaste este script anteriormente, debes eliminar los archivos creados, ya que pig no sobreescribire y obtendrás un error:

```bash
hdfs dfs -rm -r /datos/processing/
```

Para salirse del contenedor:
```bash
exit
```

Si quieres obtener los resultados para poder analizarlos, estos se deben mover a tu máquina y así poder hacer uso de ellos fuera de los contenedores:

1. Entrar a contenedor de hadoop:
```bash
docker exec -it distribuidos_hadoop bash
```

2. Extraer la carpeta con los resultados de processing:
```bash
hdfs dfs -get /datos/processing/ /resultados
exit
```

3. Mover la carpeta a tu máquina local para poder visualizarlos y trabajar con ellos:
```bash
docker cp distribuidos_hadoop:/resultados ./data_host/resultados
```

## Entrega 3