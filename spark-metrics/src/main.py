from pyspark.sql import SparkSession
from pyspark import StorageLevel

from config import (
    SPARK_APP_NAME,
    SPARK_MASTER,
    NUM_PARTITIONS
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


def ejecutar_procesamiento(sc):

    # 1. Cargar partidos desde MongoDB

    partidos = cargar_partidos()

    if not partidos:
        print("No existen partidos para procesar.")
        return

    # 2. Crear RDD inicial

    partidos_rdd = sc.parallelize(
        partidos,
        NUM_PARTITIONS
    )

    # 3. Limpieza distribuida

    partidos_validos = partidos_rdd.filter(
        partido_valido
    )

    partidos_limpios = partidos_validos.map(
        normalizar_partido
    ).persist(StorageLevel.MEMORY_AND_DISK)

    # 4. Verificar partidos válidos

    cantidad_validos = partidos_limpios.count()

    if cantidad_validos == 0:
        print("No existen partidos válidos para analizar.")
        partidos_limpios.unpersist()
        return

    # 5. Generar contribuciones

    contribuciones_rdd = partidos_limpios.flatMap(
        generar_contribuciones
    ).persist(StorageLevel.MEMORY_AND_DISK)

    # 6. Calcular estadísticas generales

    estadisticas_rdd = reducir_contribuciones(
        contribuciones_rdd
    ).persist(StorageLevel.MEMORY_AND_DISK)

    try:

        # ==================================================
        # RESULTADOS GENERALES
        # ==================================================

        print("\n========== RESULTADOS GENERALES ==========")

        print(f"Partidos originales: {len(partidos)}")
        print(f"Partidos válidos: {cantidad_validos}")

        print(
            f"Contribuciones generadas: "
            f"{contribuciones_rdd.count()}"
        )

        # ==================================================
        # CONSULTA 1
        # ==================================================

        print("\n========== CONSULTA 1 ==========")
        print("ESTADÍSTICAS POR EQUIPO")

        resultado = consulta_estadisticas_equipo(
            estadisticas_rdd
        )

        for equipo, metricas in resultado.collect():
            print(equipo, metricas)

        # ==================================================
        # CONSULTA 2
        # ==================================================

        print("\n========== CONSULTA 2 ==========")
        print("GOLES POR EQUIPO")

        resultado = consulta_goles_equipo(
            estadisticas_rdd
        )

        for equipo, metricas in resultado.collect():
            print(equipo, metricas)

        # ==================================================
        # CONSULTA 3
        # ==================================================

        print("\n========== CONSULTA 3 ==========")
        print("PUNTOS Y RENDIMIENTO")

        resultado = consulta_puntos_rendimiento(
            estadisticas_rdd
        )

        for equipo, metricas in resultado.collect():
            print(equipo, metricas)

        # ==================================================
        # CONSULTA 4
        # ==================================================

        print("\n========== CONSULTA 4 ==========")
        print("DISTRIBUCIÓN DE RESULTADOS")

        resultado = dict(
            consulta_distribucion_resultados(
                partidos_limpios
            ).collect()
        )

        # Mostrar siempre las tres categorías

        resultado_completo = {
            "victorias_local": resultado.get(
                "victorias_local", 0
            ),
            "victorias_visitante": resultado.get(
                "victorias_visitante", 0
            ),
            "empates": resultado.get(
                "empates", 0
            )
        }

        for categoria, cantidad in resultado_completo.items():
            print(f"{categoria}: {cantidad}")

        # ==================================================
        # CONSULTA 5
        # ==================================================

        print("\n========== CONSULTA 5 ==========")
        print("PROMEDIO DE GOLES")

        resultado = consulta_promedio_goles(
            partidos_limpios
        )

        print(resultado)

        # ==================================================
        # CONSULTA 6
        # ==================================================

        print("\n========== CONSULTA 6 ==========")
        print("PARTIDOS POR PERIODO")

        print("\nPartidos por mes:")

        resultado = consulta_partidos_por_periodo(
            partidos_limpios,
            periodo="mes"
        )

        for periodo, cantidad in resultado.collect():
            print(periodo, cantidad)

        print("\nPartidos por año:")

        resultado = consulta_partidos_por_periodo(
            partidos_limpios,
            periodo="anio"
        )

        for periodo, cantidad in resultado.collect():
            print(periodo, cantidad)

        print("\nPartidos por temporada:")

        resultado = consulta_partidos_por_periodo(
            partidos_limpios,
            periodo="temporada"
        )

        for periodo, cantidad in resultado.collect():
            print(periodo, cantidad)

        # ==================================================
        # CONSULTA 7
        # ==================================================

        print("\n========== CONSULTA 7 ==========")
        print("RENDIMIENTO OFENSIVO")

        resultado = consulta_rendimiento_ofensivo(
            contribuciones_rdd,
            top_n=10
        )

        for equipo, goles in resultado:
            print(f"{equipo}: {goles} goles")

        # ==================================================
        # CONSULTA 8
        # ==================================================

        print("\n========== CONSULTA 8 ==========")
        print("PARTIDOS CON MÁS GOLES")

        resultado = consulta_partidos_mas_goles(
            partidos_limpios,
            top_n=10
        )

        for partido in resultado:

            total_goles = (
                partido["goles_local"]
                + partido["goles_visitante"]
            )

            print(
                f"ID: {partido['match_id']} | "
                f"{partido['equipo_local']} "
                f"{partido['goles_local']} - "
                f"{partido['goles_visitante']} "
                f"{partido['equipo_visitante']} | "
                f"Total goles: {total_goles}"
            )

    finally:

        # Liberar memoria de los RDD persistidos

        estadisticas_rdd.unpersist()
        contribuciones_rdd.unpersist()
        partidos_limpios.unpersist()


def main():

    spark = (
        SparkSession.builder
        .appName(SPARK_APP_NAME)
        .master(SPARK_MASTER)
        .getOrCreate()
    )

    try:

        ejecutar_procesamiento(
            spark.sparkContext
        )

    finally:

        spark.stop()


if __name__ == "__main__":
    main()