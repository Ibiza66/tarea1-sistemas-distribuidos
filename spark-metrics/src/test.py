from pyspark.sql import SparkSession

from config import (
    SPARK_APP_NAME,
    SPARK_MASTER,
    NUM_PARTITIONS
)

from preprocessing import (
    partido_valido,
    normalizar_partido
)

from transformation import generar_contribuciones

from analytics import reducir_contribuciones


def ejecutar_procesamiento(sc):

    # 1. Datos de prueba
    partidos = [
        {
            "match_id": "p1",
            "fecha": "2026-08-01",
            "temporada": "2026",
            "competicion": "Primera División",
            "equipo_local": "Colo Colo",
            "equipo_visitante": "U. de Chile",
            "goles_local": 2,
            "goles_visitante": 1,
            "estado": "Finalizado"
        },
        {
            "match_id": "p2",
            "fecha": "2026-08-02",
            "temporada": "2026",
            "competicion": "Primera División",
            "equipo_local": "Universidad de Chile",
            "equipo_visitante": "U. Católica",
            "goles_local": 0,
            "goles_visitante": 0,
            "estado": "Finalizado"
        },
        {
            "match_id": "p3",
            "fecha": "2026-08-03",
            "temporada": "2026",
            "competicion": "Primera División",
            "equipo_local": "Colo-Colo",
            "equipo_visitante": "Universidad Católica",
            "goles_local": 3,
            "goles_visitante": 1,
            "estado": "Finalizado"
        },
        {
            "match_id": "p4",
            "fecha": "2026-08-04",
            "temporada": "2026",
            "competicion": "Primera División",
            "equipo_local": "Colo-Colo",
            "equipo_visitante": "Universidad de Chile",
            "goles_local": 1,
            "goles_visitante": 0,
            "estado": "En juego"
        }
    ]

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
    )

    # 4. Generar contribuciones
    contribuciones_rdd = partidos_limpios.flatMap(
        generar_contribuciones
    )

    # 5. Agregar estadísticas
    estadisticas_rdd = reducir_contribuciones(
        contribuciones_rdd
    )

    # 6. Mostrar resultados
    print("\n========== RESULTADOS DE LA PRUEBA ==========")

    print(f"Partidos originales: {len(partidos)}")

    print(
        f"Partidos válidos: {partidos_limpios.count()}"
    )

    print(
        f"Contribuciones generadas: {contribuciones_rdd.count()}"
    )

    print("\n========== ESTADÍSTICAS POR EQUIPO ==========")

    for clave, estadisticas in sorted(estadisticas_rdd.collect()):
        print(f"\nEquipo: {clave[0]}")
        print(f"Temporada: {clave[1]}")
        print(f"Competición: {clave[2]}")

        for nombre, valor in estadisticas.items():
            print(f"{nombre}: {valor}")


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