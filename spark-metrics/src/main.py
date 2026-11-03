from pyspark.sql import SparkSession
from pyspark import StorageLevel

from config import (
    SPARK_APP_NAME,
    SPARK_MASTER,
    NUM_PARTITIONS
)

from mongo_reader import cargar_partidos
from mongo_writer import guardar_resultados

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

        resultados = {}

        # ==================================================
        # CONSULTA 1: ESTADÍSTICAS POR EQUIPO
        # ==================================================

        consulta_1 = consulta_estadisticas_equipo(
            estadisticas_rdd
        ).collect()

        resultados["consulta_1_estadisticas_equipo"] = [
            {
                "equipo": clave[0],
                "temporada": clave[1],
                "competicion": clave[2],
                "metricas": metricas
            }
            for clave, metricas in consulta_1
        ]

        # ==================================================
        # CONSULTA 2: GOLES POR EQUIPO
        # ==================================================

        consulta_2 = consulta_goles_equipo(
            estadisticas_rdd
        ).collect()

        resultados["consulta_2_goles_equipo"] = [
            {
                "equipo": clave[0],
                "temporada": clave[1],
                "competicion": clave[2],
                "metricas": metricas
            }
            for clave, metricas in consulta_2
        ]

        # ==================================================
        # CONSULTA 3: PUNTOS Y RENDIMIENTO
        # ==================================================

        consulta_3 = consulta_puntos_rendimiento(
            estadisticas_rdd
        ).collect()

        resultados["consulta_3_puntos_rendimiento"] = [
            {
                "equipo": clave[0],
                "temporada": clave[1],
                "competicion": clave[2],
                "metricas": metricas
            }
            for clave, metricas in consulta_3
        ]

        # ==================================================
        # CONSULTA 4: DISTRIBUCIÓN DE RESULTADOS
        # ==================================================

        consulta_4 = dict(
            consulta_distribucion_resultados(
                partidos_limpios
            ).collect()
        )

        resultados["consulta_4_distribucion_resultados"] = [
            {
                "resultado": categoria,
                "cantidad": consulta_4.get(categoria, 0)
            }
            for categoria in [
                "victorias_local",
                "victorias_visitante",
                "empates"
            ]
        ]

        # ==================================================
        # CONSULTA 5: PROMEDIO DE GOLES
        # ==================================================

        consulta_5 = consulta_promedio_goles(
            partidos_limpios
        )

        resultados["consulta_5_promedio_goles"] = [
            consulta_5
        ]

        # ==================================================
        # CONSULTA 6: PARTIDOS POR PERIODO
        # ==================================================

        resultados_periodos = []

        for tipo_periodo in ["mes", "anio", "temporada"]:

            consulta_6 = consulta_partidos_por_periodo(
                partidos_limpios,
                periodo=tipo_periodo
            ).collect()

            for periodo, cantidad in consulta_6:

                resultados_periodos.append({
                    "tipo_periodo": tipo_periodo,
                    "periodo": periodo,
                    "cantidad_partidos": cantidad
                })

        resultados["consulta_6_partidos_por_periodo"] = (
            resultados_periodos
        )

        # ==================================================
        # CONSULTA 7: RENDIMIENTO OFENSIVO
        # ==================================================

        consulta_7 = consulta_rendimiento_ofensivo(
            contribuciones_rdd,
            top_n=10
        )

        resultados["consulta_7_rendimiento_ofensivo"] = [
            {
                "equipo": equipo,
                "goles_anotados": goles
            }
            for equipo, goles in consulta_7
        ]

        # ==================================================
        # CONSULTA 8: PARTIDOS CON MÁS GOLES
        # ==================================================

        consulta_8 = consulta_partidos_mas_goles(
            partidos_limpios,
            top_n=10
        )

        resultados["consulta_8_partidos_mas_goles"] = []

        for partido in consulta_8:

            documento = dict(partido)

            documento["total_goles"] = (
                partido["goles_local"]
                + partido["goles_visitante"]
            )

            resultados[
                "consulta_8_partidos_mas_goles"
            ].append(documento)

        # ==================================================
        # MOSTRAR Y GUARDAR RESULTADOS
        # ==================================================

        print("\n========== RESUMEN DE CONSULTAS ==========")

        for nombre, datos in resultados.items():
            print(f"{nombre}: {len(datos)} registros")

        print("\n========== GUARDANDO EN MONGODB ==========")

        guardar_resultados(resultados)

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