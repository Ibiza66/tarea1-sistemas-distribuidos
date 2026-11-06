from pyspark.sql import SparkSession
from pyspark import StorageLevel

from config import SPARK_APP_NAME, SPARK_MASTER
from mongo_reader import cargar_partidos

from preprocessing import (
    partido_valido,
    normalizar_partido
)

from transformation import generar_contribuciones

from analytics import (
    reducir_contribuciones,
    consulta_estadisticas_equipo,
    consulta_goles_equipo,
    consulta_puntos_rendimiento,
    consulta_distribucion_resultados,
    consulta_promedio_goles,
    consulta_partidos_por_periodo,
    consulta_rendimiento_ofensivo,
    consulta_partidos_mas_goles
)


def ordenar_rdd(rdd):
    return sorted(
        rdd.collect(),
        key=lambda x: repr(x)
    )


def ejecutar_consultas(sc, partidos, particiones):

    partidos_rdd = sc.parallelize(
        partidos,
        particiones
    )

    partidos_limpios = (
        partidos_rdd
        .filter(partido_valido)
        .map(normalizar_partido)
        .persist(StorageLevel.MEMORY_AND_DISK)
    )

    partidos_limpios.count()

    contribuciones_rdd = (
        partidos_limpios
        .flatMap(generar_contribuciones)
        .persist(StorageLevel.MEMORY_AND_DISK)
    )

    contribuciones_rdd.count()

    estadisticas_rdd = (
        reducir_contribuciones(contribuciones_rdd)
        .persist(StorageLevel.MEMORY_AND_DISK)
    )

    estadisticas_rdd.count()

    resultados = {
        "consulta_1": ordenar_rdd(
            consulta_estadisticas_equipo(estadisticas_rdd)
        ),

        "consulta_2": ordenar_rdd(
            consulta_goles_equipo(estadisticas_rdd)
        ),

        "consulta_3": ordenar_rdd(
            consulta_puntos_rendimiento(estadisticas_rdd)
        ),

        "consulta_4": ordenar_rdd(
            consulta_distribucion_resultados(partidos_limpios)
        ),

        "consulta_5": consulta_promedio_goles(
            partidos_limpios
        ),

        "consulta_6_mes": ordenar_rdd(
            consulta_partidos_por_periodo(
                partidos_limpios,
                "mes"
            )
        ),

        "consulta_6_anio": ordenar_rdd(
            consulta_partidos_por_periodo(
                partidos_limpios,
                "anio"
            )
        ),

        "consulta_6_temporada": ordenar_rdd(
            consulta_partidos_por_periodo(
                partidos_limpios,
                "temporada"
            )
        ),

        "consulta_7": consulta_rendimiento_ofensivo(
            contribuciones_rdd,
            top_n=10
        ),

        "consulta_8": consulta_partidos_mas_goles(
            partidos_limpios,
            top_n=10
        )
    }

    partidos_limpios.unpersist()
    contribuciones_rdd.unpersist()
    estadisticas_rdd.unpersist()

    return resultados


def main():

    spark = (
        SparkSession.builder
        .appName(f"{SPARK_APP_NAME}-ValidacionParticiones")
        .master(SPARK_MASTER)
        .getOrCreate()
    )

    sc = spark.sparkContext

    try:

        partidos = cargar_partidos()

        resultados = {}

        for particiones in (1, 2, 4):

            print(
                f"\n========== {particiones} PARTICION(ES) =========="
            )

            resultados[particiones] = ejecutar_consultas(
                sc,
                partidos,
                particiones
            )

        referencia = resultados[1]

        print("\n========== COMPARACION ==========")

        todo_igual = True

        for particiones in (2, 4):

            iguales = (
                resultados[particiones] == referencia
            )

            print(
                f"1 particion vs {particiones} particiones: "
                f"{'IGUALES' if iguales else 'DIFERENTES'}"
            )

            if not iguales:
                todo_igual = False

        print("\n========== RESULTADO FINAL ==========")

        if todo_igual:
            print(
                "Todas las consultas mantienen los mismos "
                "resultados con 1, 2 y 4 particiones."
            )
        else:
            print(
                "Se detectaron diferencias entre particiones."
            )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()