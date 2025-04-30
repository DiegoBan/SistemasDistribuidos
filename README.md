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



##  Sistema de Cache


