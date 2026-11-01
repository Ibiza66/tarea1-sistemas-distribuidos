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