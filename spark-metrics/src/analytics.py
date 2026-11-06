from datetime import datetime, date


# ==========================================================
# AGREGACION GENERAL
# ==========================================================

def reducir_contribuciones(contribuciones_rdd):

    def convertir_metricas(contribucion):

        resultado = contribucion["resultado"]

        return {
            "partidos_disputados": 1,
            "victorias": int(resultado == "Victoria"),
            "derrotas": int(resultado == "Derrota"),
            "empates": int(resultado == "Empate"),
            "goles_favor": contribucion["goles_favor"],
            "goles_contra": contribucion["goles_contra"],
            "puntos": contribucion["puntos"]
        }

    def sumar_metricas(a, b):

        return {
            clave: a[clave] + b[clave]
            for clave in a
        }

    metricas_rdd = contribuciones_rdd.mapValues(
        convertir_metricas
    )

    estadisticas_rdd = metricas_rdd.reduceByKey(
        sumar_metricas
    )

    def calcular_metricas_finales(registro):

        equipo, metricas = registro

        partidos = metricas["partidos_disputados"]

        metricas["diferencia_goles"] = (
            metricas["goles_favor"] - metricas["goles_contra"]
        )

        metricas["porcentaje_victorias"] = round(
            metricas["victorias"] / partidos * 100,
            2
        )

        metricas["promedio_puntos_partido"] = round(
            metricas["puntos"] / partidos,
            2
        )

        return equipo, metricas

    return estadisticas_rdd.map(
        calcular_metricas_finales
    )


# ==========================================================
# CONSULTA 1: ESTADISTICAS POR EQUIPO
# ==========================================================

def consulta_estadisticas_equipo(estadisticas_rdd):

    return estadisticas_rdd.mapValues(
        lambda m: {
            "partidos_disputados": m["partidos_disputados"],
            "victorias": m["victorias"],
            "empates": m["empates"],
            "derrotas": m["derrotas"]
        }
    )


# ==========================================================
# CONSULTA 2: GOLES POR EQUIPO
# ==========================================================

def consulta_goles_equipo(estadisticas_rdd):

    return estadisticas_rdd.mapValues(
        lambda m: {
            "goles_favor": m["goles_favor"],
            "goles_contra": m["goles_contra"],
            "diferencia_goles": m["diferencia_goles"]
        }
    )


# ==========================================================
# CONSULTA 3: PUNTOS Y RENDIMIENTO
# ==========================================================

def consulta_puntos_rendimiento(estadisticas_rdd):

    return estadisticas_rdd.mapValues(
        lambda m: {
            "puntos": m["puntos"],
            "porcentaje_victorias": m["porcentaje_victorias"],
            "promedio_puntos_partido":
                m["promedio_puntos_partido"]
        }
    )


# ==========================================================
# CONSULTA 4: DISTRIBUCION DE RESULTADOS
# ==========================================================

def consulta_distribucion_resultados(partidos_rdd):

    def clasificar_resultado(partido):

        goles_local = partido["goles_local"]
        goles_visitante = partido["goles_visitante"]

        estado = str(partido["estado"]).strip().casefold()

        if estado == "finalizado_tras_penales":

            penales_local = partido["penales_local"]
            penales_visitante = partido["penales_visitante"]

            if penales_local > penales_visitante:
                resultado = "victorias_local"
            else:
                resultado = "victorias_visitante"

        elif goles_local > goles_visitante:
            resultado = "victorias_local"

        elif goles_local < goles_visitante:
            resultado = "victorias_visitante"

        else:
            resultado = "empates"

        return resultado, 1

    return (
        partidos_rdd
        .map(clasificar_resultado)
        .reduceByKey(lambda a, b: a + b)
    )

# ==========================================================
# CONSULTA 5: PROMEDIO DE GOLES
# ==========================================================

def consulta_promedio_goles(partidos_rdd):

    def obtener_goles(partido):
        total_goles = (
            partido["goles_local"]
            + partido["goles_visitante"]
        )

        return total_goles, 1

    def sumar_totales(a, b):
        return (
            a[0] + b[0],
            a[1] + b[1]
        )

    resultado = partidos_rdd.map(
        obtener_goles
    ).fold(
        (0, 0),
        sumar_totales
    )

    total_goles, total_partidos = resultado

    if total_partidos == 0:
        return {
            "partidos_analizados": 0,
            "goles_totales": 0,
            "promedio_goles": 0
        }

    return {
        "partidos_analizados": total_partidos,
        "goles_totales": total_goles,
        "promedio_goles": round(
            total_goles / total_partidos,
            2
        )
    }


# ==========================================================
# CONSULTA 6: PARTIDOS POR PERIODO
# ==========================================================

def obtener_fecha(fecha):

    if isinstance(fecha, datetime):
        return fecha

    if isinstance(fecha, date):
        return datetime.combine(fecha, datetime.min.time())

    if isinstance(fecha, str):

        formatos = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%d-%m-%Y",
            "%d/%m/%Y"
        ]

        for formato in formatos:

            try:
                return datetime.strptime(fecha, formato)

            except ValueError:
                continue

        try:
            return datetime.fromisoformat(
                fecha.replace("Z", "+00:00")
            )

        except ValueError:
            raise ValueError(
                f"Formato de fecha no reconocido: {fecha}"
            )

    raise ValueError(
        f"Tipo de fecha no válido: {type(fecha)}"
    )


def consulta_partidos_por_periodo(
    partidos_rdd,
    periodo="mes"
):

    if periodo not in ("mes", "anio", "temporada"):
        raise ValueError(
            "El periodo debe ser: mes, anio o temporada"
        )

    def obtener_periodo(partido):

        if periodo == "temporada":

            clave = str(partido["temporada"])

        else:

            fecha = obtener_fecha(partido["fecha"])

            if periodo == "mes":
                clave = fecha.strftime("%Y-%m")

            else:
                clave = fecha.strftime("%Y")

        return clave, 1

    return (
        partidos_rdd
        .map(obtener_periodo)
        .reduceByKey(lambda a, b: a + b)
        .sortByKey()
    )


# ==========================================================
# CONSULTA 7: RENDIMIENTO OFENSIVO
# ==========================================================

def consulta_rendimiento_ofensivo(
    contribuciones_rdd,
    top_n=None
):
    goles_rdd = contribuciones_rdd.map(
        lambda registro: (
            registro[0][0],
            registro[1]["goles_favor"]
        )
    )

    goles_por_equipo = goles_rdd.reduceByKey(
        lambda a, b: a + b
    )

    if top_n is not None:
        return goles_por_equipo.takeOrdered(
            top_n,
            key=lambda registro: (-registro[1], registro[0])
        )

    return goles_por_equipo.sortBy(
        lambda registro: (-registro[1], registro[0])
    )


# ==========================================================
# CONSULTA 8: PARTIDOS CON MAS GOLES
# ==========================================================

def consulta_partidos_mas_goles(
    partidos_rdd,
    top_n=10
):

    def obtener_total_goles(partido):

        return (
            partido["goles_local"]
            + partido["goles_visitante"]
        )

    def clave_orden(partido):

        total = obtener_total_goles(partido)

        return (
            -total,
            str(partido["match_id"])
        )

    return partidos_rdd.takeOrdered(
        top_n,
        key=clave_orden
    )