from time import perf_counter

from pyspark.sql import SparkSession
from pyspark import StorageLevel

from config import (
    SPARK_APP_NAME,
    SPARK_MASTER
)

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


PARTICIONES = 1
REPETICIONES = 3


def medir(funcion):

    tiempos = []

    for _ in range(REPETICIONES):

        inicio = perf_counter()
        funcion()
        fin = perf_counter()

        tiempos.append(fin - inicio)

    return sum(tiempos) / len(tiempos)


def preparar_rdds(sc, partidos):

    partidos_rdd = sc.parallelize(
        partidos,
        PARTICIONES
    )

    partidos_limpios = (
        partidos_rdd
        .filter(partido_valido)
        .map(normalizar_partido)
        .persist(StorageLevel.MEMORY_AND_DISK)
    )

    cantidad_validos = partidos_limpios.count()

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

    return (
        partidos_limpios,
        contribuciones_rdd,
        estadisticas_rdd,
        cantidad_validos
    )


def medir_consultas(
    partidos_limpios,
    contribuciones_rdd,
    estadisticas_rdd
):

    resultados = {}

    resultados["consulta_1"] = medir(
        lambda: consulta_estadisticas_equipo(
            estadisticas_rdd
        ).collect()
    )

    resultados["consulta_2"] = medir(
        lambda: consulta_goles_equipo(
            estadisticas_rdd
        ).collect()
    )

    resultados["consulta_3"] = medir(
        lambda: consulta_puntos_rendimiento(
            estadisticas_rdd
        ).collect()
    )

    resultados["consulta_4"] = medir(
        lambda: consulta_distribucion_resultados(
            partidos_limpios
        ).collect()
    )

    resultados["consulta_5"] = medir(
        lambda: consulta_promedio_goles(
            partidos_limpios
        )
    )

    def ejecutar_consulta_6():

        for periodo in ["mes", "anio", "temporada"]:
            consulta_partidos_por_periodo(
                partidos_limpios,
                periodo=periodo
            ).collect()

    resultados["consulta_6"] = medir(
        ejecutar_consulta_6
    )

    resultados["consulta_7"] = medir(
        lambda: consulta_rendimiento_ofensivo(
            contribuciones_rdd,
            top_n=10
        )
    )

    resultados["consulta_8"] = medir(
        lambda: consulta_partidos_mas_goles(
            partidos_limpios,
            top_n=10
        )
    )

    return resultados


def main():

    spark = (
        SparkSession.builder
        .appName(f"{SPARK_APP_NAME}-BenchmarkVolumen")
        .master(SPARK_MASTER)
        .getOrCreate()
    )

    sc = spark.sparkContext

    try:

        print(
            "\n========== BENCHMARK N / N/2 / N/4 =========="
        )

        # Calentamiento de Spark
        sc.parallelize([1, 2, 3], 1).count()

        partidos = cargar_partidos()

        # Orden determinista para que los subconjuntos
        # sean reproducibles.
        partidos = sorted(
            partidos,
            key=lambda p: str(p["match_id"])
        )

        n = len(partidos)

        tamanos = [
            ("N", n),
            ("N/2", n // 2),
            ("N/4", n // 4)
        ]

        for nombre, tamano in tamanos:

            print(
                f"\n========== {nombre}: "
                f"{tamano} PARTIDOS =========="
            )

            subconjunto = partidos[:tamano]

            (
                partidos_limpios,
                contribuciones_rdd,
                estadisticas_rdd,
                cantidad_validos
            ) = preparar_rdds(
                sc,
                subconjunto
            )

            print(
                f"Partidos válidos: {cantidad_validos}"
            )

            tiempos = medir_consultas(
                partidos_limpios,
                contribuciones_rdd,
                estadisticas_rdd
            )

            for consulta, tiempo in tiempos.items():

                print(
                    f"{consulta}: "
                    f"{tiempo:.6f} s"
                )

            partidos_limpios.unpersist()
            contribuciones_rdd.unpersist()
            estadisticas_rdd.unpersist()

    finally:
        spark.stop()


if __name__ == "__main__":
    main()