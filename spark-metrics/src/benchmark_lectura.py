from time import perf_counter
from statistics import mean

from pyspark.sql import SparkSession

from config import (
    SPARK_APP_NAME,
    SPARK_MASTER
)

from mongo_reader import cargar_partidos


REPETICIONES = 3
PARTICIONES = 1


def main():

    spark = (
        SparkSession.builder
        .appName(f"{SPARK_APP_NAME}-BenchmarkLectura")
        .master(SPARK_MASTER)
        .getOrCreate()
    )

    sc = spark.sparkContext

    tiempos_mongodb = []
    tiempos_spark = []
    tiempos_totales = []

    try:

        print(
            "\n========== BENCHMARK LECTURA MONGODB -> SPARK =========="
        )

        print("Realizando ejecucion de calentamiento...")

        partidos_warmup = cargar_partidos()

        rdd_warmup = sc.parallelize(
            partidos_warmup,
            PARTICIONES
        )

        rdd_warmup.count()

        print("Calentamiento completado.\n")

        for repeticion in range(1, REPETICIONES + 1):

            # -------------------------------------------------
            # Fase 1: lectura desde MongoDB
            # -------------------------------------------------

            inicio_mongodb = perf_counter()

            partidos = cargar_partidos()

            fin_mongodb = perf_counter()

            tiempo_mongodb = (
                fin_mongodb - inicio_mongodb
            )

            # -------------------------------------------------
            # Fase 2: creación y materialización del RDD
            # -------------------------------------------------

            inicio_spark = perf_counter()

            partidos_rdd = sc.parallelize(
                partidos,
                PARTICIONES
            )

            cantidad = partidos_rdd.count()

            fin_spark = perf_counter()

            tiempo_spark = (
                fin_spark - inicio_spark
            )

            tiempo_total = (
                tiempo_mongodb + tiempo_spark
            )

            porcentaje_mongodb = (
                tiempo_mongodb
                / tiempo_total
                * 100
            )

            porcentaje_spark = (
                tiempo_spark
                / tiempo_total
                * 100
            )

            tiempos_mongodb.append(
                tiempo_mongodb
            )

            tiempos_spark.append(
                tiempo_spark
            )

            tiempos_totales.append(
                tiempo_total
            )

            print(
                f"Repeticion {repeticion}: "
                f"{cantidad} documentos"
            )

            print(
                f"  MongoDB / E/S: "
                f"{tiempo_mongodb:.6f} s "
                f"({porcentaje_mongodb:.2f}%)"
            )

            print(
                f"  Spark RDD:     "
                f"{tiempo_spark:.6f} s "
                f"({porcentaje_spark:.2f}%)"
            )

            print(
                f"  Total:         "
                f"{tiempo_total:.6f} s"
            )

            print()

        promedio_mongodb = mean(
            tiempos_mongodb
        )

        promedio_spark = mean(
            tiempos_spark
        )

        promedio_total = mean(
            tiempos_totales
        )

        porcentaje_promedio_mongodb = (
            promedio_mongodb
            / promedio_total
            * 100
        )

        porcentaje_promedio_spark = (
            promedio_spark
            / promedio_total
            * 100
        )

        print(
            "========== RESULTADO PROMEDIO =========="
        )

        print(
            f"Repeticiones: {REPETICIONES}"
        )

        print(
            f"Documentos por ejecucion: {cantidad}"
        )

        print(
            f"MongoDB / E/S: "
            f"{promedio_mongodb:.6f} s "
            f"({porcentaje_promedio_mongodb:.2f}%)"
        )

        print(
            f"Spark RDD:     "
            f"{promedio_spark:.6f} s "
            f"({porcentaje_promedio_spark:.2f}%)"
        )

        print(
            f"Tiempo total:  "
            f"{promedio_total:.6f} s"
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()