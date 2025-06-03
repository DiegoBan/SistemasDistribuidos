eventos = LOAD 'hdfs://hadoop:9000/datos/alertas_output/part-r-00000' USING PigStorage(',') AS (
    uuid:chararray,
    country:chararray,
    city:chararray,
    street:chararray,
    type:chararray,
    subtype:chararray,
    longitude:double,
    latitude:double,
    lat_norm:double,
    lon_norm:double,
    pubMillis:long,
    fecha_actual:chararray,
    fecha_dt:chararray,
    bloque_horario:int,
    lat_grid:int,
    lon_grid:int
);

atascos = LOAD 'hdfs://hadoop:9000/datos/jams_output/part-r-00000' USING PigStorage(',') AS (
    uuid:chararray,
    severity:int,
    country:chararray,
    length:int,
    endnode:chararray,
    speed:double,
    city:chararray,
    street:chararray,
    type:chararray,
    longitude:double,
    latitude:double,
    lat_norm:double,
    lon_norm:double,
    pubMillis:long,
    fecha_actual:chararray,
    fecha_dt:chararray,
    bloque_horario:int,
    lat_grid:int,
    lon_grid:int
);

frecuencia_comuna_tipo = FOREACH (GROUP eventos BY (city, type)) GENERATE
    FLATTEN(group) AS (comuna, tipo),
    COUNT(eventos) AS cantidad;
STORE frecuencia_comuna_tipo INTO 'hdfs://hadoop:9000/datos/frecuencia_comuna_tipo' USING PigStorage(',');


frecuencia_bloque = FOREACH (GROUP eventos BY bloque_horario) GENERATE
    group AS bloque_horario,
    COUNT(eventos) AS cantidad;
STORE frecuencia_bloque INTO 'hdfs://hadoop:9000/datos/frecuencia_bloque' USING PigStorage(',');


eventos_por_comuna = FOREACH (GROUP eventos BY city) GENERATE
    group AS comuna,
    COUNT(eventos) AS cantidad;
eventos_por_comuna_ord = ORDER eventos_por_comuna BY cantidad DESC;
STORE eventos_por_comuna_ord INTO 'hdfs://hadoop:9000/datos/eventos_por_comuna' USING PigStorage(',');


accidentes = FILTER eventos BY type == 'ACCIDENT';
accidentes_por_comuna = FOREACH (GROUP accidentes BY city) GENERATE
    group AS comuna,
    COUNT(accidentes) AS cantidad;
accidentes_ordenados = ORDER accidentes_por_comuna BY cantidad DESC;
STORE accidentes_ordenados INTO 'hdfs://hadoop:9000/datos/accidentes_por_comuna' USING PigStorage(',');

eventos_por_calle = FOREACH (GROUP eventos BY street) GENERATE
    group AS calle,
    COUNT(eventos) AS cantidad;
calles_ordenadas = ORDER eventos_por_calle BY cantidad DESC;
STORE calles_ordenadas INTO 'hdfs://hadoop:9000/datos/eventos_por_calle' USING PigStorage(',');


atascos_por_ciudad = FOREACH (GROUP atascos BY city) GENERATE
    group AS ciudad,
    SUM(atascos.length) AS largo_total,
    COUNT(atascos) AS num_atascos;
atascos_ordenados = ORDER atascos_por_ciudad BY largo_total DESC;
STORE atascos_ordenados INTO 'hdfs://hadoop:9000/datos/atascos_por_ciudad' USING PigStorage(',');

