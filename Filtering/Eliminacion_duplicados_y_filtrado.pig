-- Cargar datos desde HDFS
eventos_crudos = LOAD 'hdfs://hadoop:9000/ruta/a/tu/archivo.csv'
    USING PigStorage(',') AS (
        uuid:chararray,
        country:chararray,
        city:chararray,
        street:chararray,
        type:chararray,
        subtype:chararray,
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
    subtype IS NOT NULL AND subtype != '' AND
    longitude IS NOT NULL AND longitude >= -180 AND longitude <= 180 AND
    latitude IS NOT NULL AND latitude >= -90 AND latitude <= 90 AND
    pubMillis IS NOT NULL;

-- Deduplicar por UUID, conservar el más reciente
agrupados_por_uuid = GROUP eventos_validos BY uuid;

eventos_deduplicados = FOREACH agrupados_por_uuid {
    ordenados = ORDER eventos_validos BY pubMillis DESC;
    primero = LIMIT ordenados 1;
    GENERATE FLATTEN(primero);
};

-- Enriquecer con fecha y calcular bloque horario
eventos_con_fecha = FOREACH eventos_deduplicados GENERATE
    *,
    ToDate(fecha_actual, 'yyyy-MM-dd''T''HH:mm:ss.SSSSSS') AS fecha_dt;

eventos_con_bloque = FOREACH eventos_con_fecha GENERATE
    *,
    (int)(GetHour(fecha_dt) / 3) AS bloque_horario;

-- Crear rejilla espacial: discretizar lat/lon para agrupar por zona
eventos_con_rejilla = FOREACH eventos_con_bloque GENERATE
    *,
    (int)(latitude * 100) AS lat_grid,    -- ~0.01 grados = ~1km
    (int)(longitude * 100) AS lon_grid;

-- Normalizar campos texto y escala latitud/longitud a [0,1]
eventos_normalizados = FOREACH eventos_con_rejilla GENERATE
    uuid,
    LOWER(country) AS country,
    LOWER(city) AS city,
    LOWER(street) AS street,
    LOWER(type) AS type,
    LOWER(subtype) AS subtype,
    longitude,
    latitude,
    (latitude + 90) / 180.0 AS lat_norm,
    (longitude + 180) / 360.0 AS lon_norm,
    pubMillis,
    fecha_actual,
    fecha_dt,
    bloque_horario,
    lat_grid,
    lon_grid;

-- Agrupar por tipo, rejilla lat/lon y bloque horario
agrupados_por_tipo_coord_bloque = GROUP eventos_normalizados BY (type, lat_grid, lon_grid, bloque_horario);

-- Homogeneizar: tomar evento más reciente por grupo
eventos_homogeneizados = FOREACH agrupados_por_tipo_coord_bloque {
    ordenados = ORDER eventos_normalizados BY pubMillis DESC;
    top_evento = LIMIT ordenados 1;
    GENERATE FLATTEN(top_evento);
};

-- Guardar resultados
STORE eventos_homogeneizados INTO 'hdfs://hadoop:9000/salida/eventos_homogeneos'
USING PigStorage(',');
