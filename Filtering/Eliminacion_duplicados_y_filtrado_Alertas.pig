eventos_crudos = LOAD '../datos/alertas.csv'
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

eventos_validos = FILTER eventos_crudos BY
    uuid IS NOT NULL AND uuid != '' AND
    country IS NOT NULL AND country != '' AND
    city IS NOT NULL AND city != '' AND
    street IS NOT NULL AND street != '' AND
    type IS NOT NULL AND type != '' AND
    subtype IS NOT NULL AND subtype != '' AND
    longitude IS NOT NULL AND longitude >= -180 AND longitude <= 180 AND
    latitude IS NOT NULL AND latitude >= -90 AND latitude <= 90 AND
    pubMillis IS NOT NULL AND
    fecha_actual IS NOT NULL;

agrupados_por_uuid = GROUP eventos_validos BY uuid;

eventos_deduplicados = FOREACH agrupados_por_uuid {
    eventos = eventos_validos;
    ordenados = ORDER eventos BY pubMillis DESC;
    primero = LIMIT ordenados 1;
    GENERATE FLATTEN(primero);
};

eventos_con_fecha = FOREACH eventos_deduplicados GENERATE
    *,
    ToDate(fecha_actual, 'yyyy-MM-dd\'T\'HH:mm:ss.SSSSSS') AS fecha_dt;

eventos_con_bloque = FOREACH eventos_con_fecha GENERATE
    *,
    (int)(GetHour(fecha_dt) / 3) AS bloque_horario;

eventos_con_rejilla = FOREACH eventos_con_bloque GENERATE
    *,
    (int)(latitude * 1000) AS lat_grid,
    (int)(longitude * 1000) AS lon_grid;

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

agrupados_por_tipo_coord_bloque = GROUP eventos_normalizados BY (type, lat_grid, lon_grid, bloque_horario);

eventos_homogeneizados = FOREACH agrupados_por_tipo_coord_bloque {
    eventos = eventos_normalizados;
    ordenados = ORDER eventos BY pubMillis DESC;
    top_evento = LIMIT ordenados 1;
    GENERATE FLATTEN(top_evento);
};

STORE eventos_homogeneizados INTO '../datos/pe' USING PigStorage(',');

eventos_crudos_atascos = LOAD '../datos/alertas.csv'
    USING PigStorage(',') AS (
        uuid:chararray,
        severity:int,
        country:chararray,
        length:int,
        endnode:chararray,
        speed:double,
        city:chararray,
        street:chararray,
        type:chararray,
        subtype:chararray,
        longitude:double,
        latitude:double,
        pubMillis:long,
        fecha_actual:chararray
    );

eventos_validos_atascos = FILTER eventos_crudos_atascos BY
    uuid IS NOT NULL AND uuid != '' AND
    severity IS NOT NULL AND severity != 0 AND
    country IS NOT NULL AND country != '' AND
    length IS NOT NULL AND length != 0 AND
    endnode IS NOT NULL AND endnode != '' AND
    speed IS NOT NULL AND speed > 0 AND
    city IS NOT NULL AND city != '' AND
    street IS NOT NULL AND street != '' AND
    type IS NOT NULL AND type != '' AND
    subtype IS NOT NULL AND subtype != '' AND
    longitude IS NOT NULL AND longitude >= -180 AND longitude <= 180 AND
    latitude IS NOT NULL AND latitude >= -90 AND latitude <= 90 AND
    pubMillis IS NOT NULL AND
    fecha_actual IS NOT NULL;

agrupados_por_uuid_atascos = GROUP eventos_validos_atascos BY uuid;

eventos_deduplicados_atascos = FOREACH agrupados_por_uuid_atascos {
    eventos = eventos_validos_atascos;
    ordenados = ORDER eventos BY pubMillis DESC;
    primero = LIMIT ordenados 1;
    GENERATE FLATTEN(primero);
};

eventos_con_fecha_atascos = FOREACH eventos_deduplicados_atascos GENERATE
    *,
    ToDate(fecha_actual, 'yyyy-MM-dd\'T\'HH:mm:ss.SSSSSS') AS fecha_dt;

eventos_con_bloque_atascos = FOREACH eventos_con_fecha_atascos GENERATE
    *,
    (int)(GetHour(fecha_dt) / 6) AS bloque_horario;

eventos_con_rejilla_atascos = FOREACH eventos_con_bloque_atascos GENERATE
    *,
    (int)(latitude * 100) AS lat_grid,
    (int)(longitude * 100) AS lon_grid;

eventos_normalizados_atascos = FOREACH eventos_con_rejilla_atascos GENERATE
    uuid,
    severity,
    LOWER(country) AS country,
    length,
    LOWER(endnode) AS endnode,
    speed,
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

agrupados_por_tipo_coord_bloque_atascos = GROUP eventos_normalizados_atascos BY (type, lat_grid, lon_grid, bloque_horario);

eventos_homogeneizados_atascos = FOREACH agrupados_por_tipo_coord_bloque_atascos {
    eventos = eventos_normalizados_atascos;
    ordenados = ORDER eventos BY pubMillis DESC;
    top_evento = LIMIT ordenados 1;
    GENERATE FLATTEN(top_evento);
};

STORE eventos_homogeneizados_atascos INTO '../datos/pe_atascos' USING PigStorage(',');
