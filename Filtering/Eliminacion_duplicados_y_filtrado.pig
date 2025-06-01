datos_brutos = LOAD 'RUTA_DEL_CSV' USING PigStorage(',') AS
(
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
    pubMillis:long
);

-- Eliminar datos incompletos
datos_sin_incompletos = FILTER datos_brutos BY
    uuid IS NOT NULL AND uuid != '' AND
    city IS NOT NULL AND city != '' AND
    street IS NOT NULL AND street != '' AND
    type IS NOT NULL AND type != '';

-- Agrupar por uuid para eliminar duplicados
datos_grupados = GROUP datos_sin_incompletos BY uuid;

-- Dentro de cada grupo, ordenar por pubMillis descendente y tomar solo el más reciente
datos_sin_duplicados = FOREACH datos_grupados {
    ordenados = ORDER datos_sin_incompletos BY pubMillis DESC;
    limit_1 = LIMIT ordenados 1;
    GENERATE FLATTEN(limit_1);
};




Extraer_fecha = 
