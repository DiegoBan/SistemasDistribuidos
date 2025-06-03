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

### Entrega 1

##  Scrapper

El scrapper obtiene información desde la página de [Waze](https://www.waze.com/es-419/live-map/), obteniendo desde cada comuna de la región metropolitana sus alertas y tráfico del momento, para posteriormente guardarlo en el Almacenamiento.
Al inicializar el entorno de docker-compose, automaticamente se realiza una ejecuión del Scrapper, añadiendo más datos a la base de datos, sin embargo, si el entorno ya está levantado y se desea realizar otra ejecución, se debe entrar a la consola del contenedor a través de:

```bash
docker exec -it Scrapper bash
```

Y ejecutar:

```bash
python Web_Scrapper.py
```

##  Almacenamiento

Para el almacenamiento se utilizó la base de datos noSQL mongoDB, a través de su imagen oficial de Docker, abriendola en el puerto "27017" y creando un volumen (para el guardado de datos local) en la carpeta "./Almacenamiento:/data/db".
Para conectarse con la consola de mongodb se puede utilizar el comando:

```bash
docker exec -it distribuidos_db mongosh
```

Para contar cuantos datos hay en una colección, se puede utilizar lo siguiente (dentro de la consola de mongo):

```bash
db.collection.countDocuments({})
```

##  Generador de Tráfico

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

##  Sistema de Cache

Utilizando Redis, se crea una memoria cache (en memoria principal), el cual puede tener distintos tamaños o política de remoción.
El tamaño de este se puede intercambiar a través de http://0.0.0.0:8000/changesize/{size} (o desde contenedores: http://cache:8000/changesize/{size}), en el cual size es un número que representa el tamaño de la memoria para cache en MB.
Por otro lado tenemos la política de remoción, las cuales son LRU (Last Recently Use) o LFU (Least Frecuently Use), estas se intercambian entre sí tan solo llamando a http://0.0.0.0:8000/changepolicy (o desde contenedores: http://cache:8000/changepolicy).

### Entrega 2

## Filtering y Homogeneización

Su utilizan distintos scripts de pig para realizar un correcto filtrado y homogenización de los datos obtenidos a través del scrapping, para obtener los datos desde la base de datos mongo en un csv que utilizará posteriormente pig, se debe insertarl el siguiente comando:

```bash
docker exec -it distribuidos_db mongoexport \
  --host localhost \
  --db SD_db \
  --collection Alertas \
  --type=csv \
  --fields uuid,country,city,street,type,subtype,location.x,location.y,pubMillis,fecha_subida \
  --out /datos/alertas.csv
```

Ahora se tiene el csv en nuestra maquina local, se debe mover a hadoop para su posterior utilización con pig

```bash
docker exec -it distribuidos_namenode bash -c "\
  hdfs dfs -mkdir -p /datos && \
  hdfs dfs -put /datos/alertas.csv /datos/alertas.csv \
"
```

## Processing
