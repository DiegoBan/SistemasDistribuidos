-- Cargar datos desde HDFS
eventos_crudos = LOAD 'hdfs://hadoop:9000/ruta/a/tu/archivo.csv'
                  USING PigStorage(',') AS (
    uuid:chararray,
    country:chararray,
    city:chararray,
    street:chararray,
    type:chararray,
    subtype:chararray,
    reportBy:chararray,
    reportRating:int,
    nThumbsUp:int,
    nComments:int,
    reliability:int,
    confidence:int,
    longitude:double,
    latitude:double,
    pubMillis:long,
    fecha_actual:chararray
);

-- Filtrar registros válidos
eventos_validos = FILTER eventos_crudos BY
    uuid IS NOT NULL AND uuid != '' AND
    city IS NOT NULL AND city != '' AND
    street IS NOT NULL AND street != '' AND
    type IS NOT NULL AND type != '' AND
    pubMillis IS NOT NULL;

-- Deduplicar por uuid, conservar evento más reciente
agrupados_por_uuid = GROUP eventos_validos BY uuid;

eventos_deduplicados = FOREACH agrupados_por_uuid {
    ordenados = ORDER eventos_validos BY pubMillis DESC;
    primero = LIMIT ordenados 1;
    GENERATE FLATTEN(primero);
};

-- Enriquecer con fecha como DATETIME y calcular bloque horario
eventos_con_fecha = FOREACH eventos_deduplicados GENERATE
    *,
    ToDate(fecha_actual, 'yyyy-MM-dd''T''HH:mm:ss.SSSSSS') AS fecha_dt;

eventos_con_bloque = FOREACH eventos_con_fecha GENERATE
    *,
    (int)(GetHour(fecha_dt) / 3) AS bloque_horario;

-- Agrupar por tipo, calle y bloque horario
agrupados_por_tipo_calle_bloque = GROUP eventos_con_bloque BY (type, street, bloque_horario);

-- Homogeneizar: conservar evento más reciente por grupo
eventos_homogeneizados = FOREACH agrupados_por_tipo_calle_bloque {
    ordenados = ORDER eventos_con_bloque BY pubMillis DESC;
    top_evento = LIMIT ordenados 1;
    GENERATE FLATTEN(top_evento);
};

-- Visualizar resultados
DUMP eventos_homogeneizados;
