import csv
import json
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import os

# Configuración de Elasticsearch
ES_HOST = 'elasticsearch'  # Nombre del servicio en Docker
ES_PORT = 9200
ES_SCHEME = 'http'

# Inicializar es como None, se configurará en main()
es = None

def process_alertas_row(row):
    """Procesa una fila del CSV de alertas y la convierte al formato adecuado"""
    processed_row = {}
    
    for key, value in row.items():
        # Limpiar nombres de columnas que empiezan con **
        clean_key = key.replace('**', '')
        
        # Convertir valores numéricos
        if clean_key in ['location.x', 'location.y']:
            try:
                processed_row[clean_key] = float(value) if value else None
            except ValueError:
                processed_row[clean_key] = None
        elif clean_key == 'pubMillis':
            try:
                processed_row[clean_key] = int(value) if value else None
                # Convertir timestamp a fecha legible si es necesario
                if processed_row[clean_key]:
                    processed_row['timestamp'] = datetime.fromtimestamp(processed_row[clean_key] / 1000).isoformat()
            except ValueError:
                processed_row[clean_key] = None
        else:
            processed_row[clean_key] = value.strip() if value else None
    
    return processed_row

def process_jams_row(row):
    """Procesa una fila del CSV de jams y la convierte al formato adecuado"""
    processed_row = {}
    
    for key, value in row.items():
        # Limpiar nombres de columnas que empiezan con **
        clean_key = key.replace('**', '')
        
        # Convertir valores numéricos
        if clean_key in ['line.0.x', 'line.0.y', 'length', 'speed']:
            try:
                processed_row[clean_key] = float(value) if value else None
            except ValueError:
                processed_row[clean_key] = None
        elif clean_key == 'severity':
            try:
                processed_row[clean_key] = int(value) if value else None
            except ValueError:
                processed_row[clean_key] = None
        elif clean_key == 'pubMillis':
            try:
                processed_row[clean_key] = int(value) if value else None
                # Convertir timestamp a fecha legible si es necesario
                if processed_row[clean_key]:
                    processed_row['timestamp'] = datetime.fromtimestamp(processed_row[clean_key] / 1000).isoformat()
            except ValueError:
                processed_row[clean_key] = None
        else:
            processed_row[clean_key] = value.strip() if value else None
    
    return processed_row

def create_index_mapping(index_name, mapping_type='alertas'):
    """Crea el mapeo del índice según el tipo de datos"""
    
    if mapping_type == 'alertas':
        mapping = {
            "mappings": {
                "properties": {
                    "uuid": {"type": "keyword"},
                    "country": {"type": "keyword"},
                    "city": {"type": "keyword"},
                    "street": {"type": "text"},
                    "type": {"type": "keyword"},
                    "subtype": {"type": "keyword"},
                    "location.x": {"type": "float"},
                    "location.y": {"type": "float"},
                    "pubMillis": {"type": "long"},
                    "fecha_subida": {"type": "keyword"},
                    "timestamp": {"type": "date"}
                }
            }
        }
    else:  # jams
        mapping = {
            "mappings": {
                "properties": {
                    "uuid": {"type": "keyword"},
                    "severity": {"type": "integer"},
                    "country": {"type": "keyword"},
                    "length": {"type": "float"},
                    "speed": {"type": "float"},
                    "city": {"type": "keyword"},
                    "street": {"type": "text"},
                    "type": {"type": "keyword"},
                    "line.0.x": {"type": "float"},
                    "line.0.y": {"type": "float"},
                    "pubMillis": {"type": "long"},
                    "fecha_subida": {"type": "keyword"},
                    "timestamp": {"type": "date"}
                }
            }
        }
    
    # Crear índice si no existe
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=mapping)
        print(f"Índice '{index_name}' creado con mapeo")
    else:
        print(f"Índice '{index_name}' ya existe")

def insert_csv_to_elasticsearch(csv_file_path, index_name, process_function, batch_size=1000):
    """Inserta datos de CSV a Elasticsearch"""
    
    if not os.path.exists(csv_file_path):
        print(f"Error: El archivo {csv_file_path} no existe")
        return
    
    docs = []
    total_docs = 0
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row_num, row in enumerate(csv_reader, 1):
                try:
                    processed_row = process_function(row)
                    
                    doc = {
                        '_index': index_name,
                        '_source': processed_row
                    }
                    docs.append(doc)
                    
                    # Insertar en lotes
                    if len(docs) >= batch_size:
                        success_count, failed_docs = bulk(es, docs, stats_only=False)
                        total_docs += success_count
                        
                        if failed_docs:
                            print(f"Fallos en lote: {len(failed_docs)}")
                        
                        docs = []  # Limpiar lista
                        print(f"Procesadas {row_num} filas, insertados {total_docs} documentos")
                
                except Exception as e:
                    print(f"Error procesando fila {row_num}: {e}")
                    continue
            
            # Insertar los documentos restantes
            if docs:
                success_count, failed_docs = bulk(es, docs, stats_only=False)
                total_docs += success_count
                
                if failed_docs:
                    print(f"Fallos en último lote: {len(failed_docs)}")
        
        print(f"✅ Completado: {total_docs} documentos insertados en '{index_name}'")
        
    except Exception as e:
        print(f"❌ Error leyendo el archivo {csv_file_path}: {e}")

def main():
    """Función principal"""
    global es
    print("🚀 Iniciando inserción de datos CSV a Elasticsearch...")
    
    # Configurar conexión a Elasticsearch
    try:
        # Opción 1: URL completa (recomendada para nuevas versiones)
        es = Elasticsearch([f'{ES_SCHEME}://{ES_HOST}:{ES_PORT}'])
        info = es.info()
        print(f"✅ Conexión a Elasticsearch exitosa - Versión: {info['version']['number']}")
    except Exception as e:
        print(f"❌ Error de conexión inicial: {e}")
        print("Intentando con configuraciones alternativas...")
        
        # Intentar configuración alternativa 1
        try:
            es = Elasticsearch(['http://elasticsearch:9200'])
            es.info()
            print("✅ Conexión alternativa 1 exitosa")
        except Exception as e2:
            # Intentar configuración alternativa 2
            try:
                es = Elasticsearch(['http://localhost:9200'])
                es.info()
                print("✅ Conexión alternativa 2 exitosa")
            except Exception as e3:
                # Intentar configuración alternativa 3
                try:
                    es = Elasticsearch(
                        hosts=[{'host': ES_HOST, 'port': ES_PORT, 'scheme': ES_SCHEME}],
                        timeout=30,
                        max_retries=10,
                        retry_on_timeout=True
                    )
                    es.info()
                    print("✅ Conexión alternativa 3 exitosa")
                except Exception as e4:
                    print(f"❌ No se pudo conectar con ninguna configuración:")
                    print(f"   Error 1: {e}")
                    print(f"   Error 2: {e2}")
                    print(f"   Error 3: {e3}")
                    print(f"   Error 4: {e4}")
                    return
    
    # Procesar alertas.csv
    print("\n📋 Procesando alertas.csv...")
    create_index_mapping('alertas', 'alertas')
    insert_csv_to_elasticsearch('alertas.csv', 'alertas', process_alertas_row)
    
    # Procesar jams.csv
    print("\n🚦 Procesando jams.csv...")
    create_index_mapping('jams', 'jams')
    insert_csv_to_elasticsearch('jams.csv', 'jams', process_jams_row)
    
    print("\n🎉 Proceso completado!")
    
    # Mostrar estadísticas
    try:
        alertas_count = es.count(index='alertas')['count']
        jams_count = es.count(index='jams')['count']
        print(f"\n📊 Estadísticas finales:")
        print(f"   - Alertas: {alertas_count} documentos")
        print(f"   - Jams: {jams_count} documentos")
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")

if __name__ == "__main__":
    main()