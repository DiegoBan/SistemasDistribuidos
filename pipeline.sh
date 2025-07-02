#!/bin/bash
set -e

wait_for_process() {
    local container=$1
    local process=$2
    local timeout=${3:-240}
    local counter=0
    
    while [ $counter -lt $timeout ]; do
        if ! docker exec $container pgrep -f "$process" > /dev/null 2>&1; then
            return 0
        fi
        sleep 2 
        ((counter+=2))
    done
    
    echo "Timeout: $process"
    exit 1
}

wait_for_file() {
    local container=$1
    local file=$2
    local timeout=${3:-240}
    local counter=0
    
    while [ $counter -lt $timeout ]; do
        if docker exec $container test -f $file 2>/dev/null; then
            return 0
        fi
        sleep 2 
        ((counter+=2))
    done
    
    echo "Timeout: $file"
    exit 1
}

# para archivos HDFS
wait_for_hdfs_file() {
    local container=$1
    local hdfs_path=$2
    local timeout=${3:-300}
    local counter=0
    
    while [ $counter -lt $timeout ]; do
        if docker exec $container hdfs dfs -test -f $hdfs_path 2>/dev/null; then
            return 0
        fi
        sleep 2 
        ((counter+=2))
    done
    
    echo "Timeout: HDFS file $hdfs_path"
    exit 1
}

echo "Iniciando pipeline..."

# 1. Scrapping
#echo "1. Ejecutando scrapper..."
#docker exec -it Scrapper python3 Web_Scrapper.py
#wait_for_process "Scrapper" "Web_Scrapper.py"

# 2. Exportar desde MongoDB
echo "2. Exportando datos desde MongoDB..."
docker exec distribuidos_db mongoexport \
    --host localhost \
    --db SD_db \
    --collection Alertas \
    --type=csv \
    --fields uuid,country,city,street,type,subtype,location.x,location.y,pubMillis,fecha_subida \
    --limit=5000 \
    --out /datos/alertas.csv > /dev/null

docker exec distribuidos_db mongoexport \
    --host localhost \
    --db SD_db \
    --collection Jams \
    --type=csv \
    --fields uuid,severity,country,length,speed,city,street,type,line.0.x,line.0.y,pubMillis,fecha_subida \
    --limit=5000 \
    --out /datos/jams.csv > /dev/null

wait_for_file "distribuidos_db" "/datos/alertas.csv"
wait_for_file "distribuidos_db" "/datos/jams.csv"

# 3. Copiar a local
echo "3. Copiando archivos a local..."
mkdir -p ./data_host
docker cp distribuidos_db:/datos/alertas.csv ./data_host/alertas.csv
docker cp distribuidos_db:/datos/jams.csv ./data_host/jams.csv

# 4. Copiar a Hadoop
echo "4. Moviendo datos a Hadoop..."
docker cp ./data_host/alertas.csv distribuidos_hadoop:/alertas.csv
docker cp ./data_host/jams.csv distribuidos_hadoop:/jams.csv

# 5. Organizar en HDFS
echo "5. Organizando en HDFS..."
docker exec distribuidos_hadoop hdfs dfs -mkdir -p /datos > /dev/null 2>&1 || true
docker exec distribuidos_hadoop hdfs dfs -copyFromLocal -f /alertas.csv /datos/alertas.csv
docker exec distribuidos_hadoop hdfs dfs -copyFromLocal -f /jams.csv /datos/jams.csv

# 6. Limpiar outputs anteriores
echo "6. Limpiando outputs anteriores..."
docker exec distribuidos_hadoop hdfs dfs -rm -r /datos/alertas_output /datos/jams_output 2>/dev/null || true
docker exec distribuidos_hadoop hdfs dfs -rm -r /datos/processing/ 2>/dev/null || true

# 7. Filtrado y eliminación de duplicados
echo "7. Ejecutando filtrado..."
docker exec -it distribuidos_pig pig -x local Eliminacion_duplicados_y_filtrado.pig
echo "Verificar que hdfs files se crearan"
wait_for_hdfs_file "distribuidos_hadoop" "/datos/alertas_output/part-r-00000"
wait_for_hdfs_file "distribuidos_hadoop" "/datos/jams_output/part-r-00000"

# 8. Extraer resultados filtrados
echo "8. Extrayendo resultados filtrados..."
docker exec distribuidos_hadoop hdfs dfs -get /datos/alertas_output/part-r-00000 /alertas_resultado.csv
docker exec distribuidos_hadoop hdfs dfs -get /datos/jams_output/part-r-00000 /jams_resultado.csv

docker cp distribuidos_hadoop:/alertas_resultado.csv ./data_host/alertas_resultado.csv
docker cp distribuidos_hadoop:/jams_resultado.csv ./data_host/jams_resultado.csv

# 9. Procesamiento de datos
echo "9. Ejecutando procesamiento..."
docker exec distribuidos_pig pig -x local Procesado_datos.pig
echo "verificando creacion frecuencia_comuna_tipo"
wait_for_hdfs_file "distribuidos_hadoop" "/datos/processing/frecuencia_comuna_tipo/part-r-00000"
echo "verificando creacion frecuencia_bloque_horario"
wait_for_hdfs_file "distribuidos_hadoop" "/datos/processing/frecuencia_bloque_horario/part-r-00000"
echo "verificando creacion eventos_por_comuna"
wait_for_hdfs_file "distribuidos_hadoop" "/datos/processing/eventos_por_comuna/part-r-00000"
echo "verificando creacion accidentes_por_comuna"
wait_for_hdfs_file "distribuidos_hadoop" "/datos/processing/accidentes_por_comuna/part-r-00000"
echo "verificando creacion eventos_por_calle"
wait_for_hdfs_file "distribuidos_hadoop" "/datos/processing/eventos_por_calle/part-r-00000"
echo "verificando creacion atascos_por_ciudad"
wait_for_hdfs_file "distribuidos_hadoop" "/datos/processing/atascos_por_ciudad/part-r-00000"

# 10. Extraer resultados finales
echo "10. Extrayendo resultados finales..."
docker exec distribuidos_hadoop hdfs dfs -get /datos/processing/ /resultados
docker cp distribuidos_hadoop:/resultados ./data_host/resultados

echo "Pipeline completado."