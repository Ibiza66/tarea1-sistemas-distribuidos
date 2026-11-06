from time import perf_counter

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

    tiempos = []

    try:

        print("\n========== BENCHMARK LECTURA MONGODB -> SPARK ==========")
        print("Realizando ejecución de calentamiento...")

        partidos_warmup = cargar_partidos()
        rdd_warmup = sc.parallelize(
            partidos_warmup,
            PARTICIONES
        )
        rdd_warmup.count()

        print("Calentamiento completado.\n")
        for repeticion in range(1, REPETICIONES + 1):

            inicio = perf_counter()

            partidos = cargar_partidos()

            partidos_rdd = sc.parallelize(
                partidos,
                PARTICIONES
            )

            cantidad = partidos_rdd.count()

            fin = perf_counter()

            tiempo = fin - inicio
            tiempos.append(tiempo)

            print(
                f"Repetición {repeticion}: "
                f"{cantidad} documentos | "
                f"{tiempo:.6f} s"
            )

        promedio = sum(tiempos) / len(tiempos)

        print("\n========== RESULTADO ==========")
        print(f"Repeticiones: {REPETICIONES}")
        print(f"Documentos por ejecución: {cantidad}")
        print(f"Tiempo promedio: {promedio:.6f} s")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()