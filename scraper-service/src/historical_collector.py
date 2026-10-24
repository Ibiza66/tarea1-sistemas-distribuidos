"""
Recolección histórica de partidos de la Liga de Primera.

Este módulo recorre distintas temporadas de Soccerway,
procesa los partidos encontrados y genera estadísticas
sobre los registros recolectados.
"""

import time

from match_parser import extraer_partidos
from mongo_storage import guardar_partidos
from render_client import obtener_html_resultados


TEMPORADAS = [
    "2015/2016",
    "2016/2017",
    2017,
    2018,
    2019,
    2020,
    2021,
    2022,
    2023,
    2024,
    2025,
]


def recolectar_partidos_historicos():
    """
    Recolecta partidos de todas las temporadas configuradas.

    Los partidos se deduplican utilizando match_id.
    """

    partidos_por_id = {}

    total_extraidos = 0

    for temporada in TEMPORADAS:
        print(
            f"Recolectando temporada {temporada}..."
        )

        resultado = obtener_html_resultados(
            temporada
        )

        partidos = extraer_partidos(
            resultado["html"],
            temporada
        )

        total_extraidos += len(partidos)

        for partido in partidos:
            match_id = partido.get("match_id")

            if match_id:
                partidos_por_id[match_id] = partido

        print(
            f"  Partidos encontrados: {len(partidos)}"
        )

        # Evita realizar solicitudes consecutivas
        # demasiado rápidas contra Soccerway.
        time.sleep(1)

    partidos_unicos = list(
        partidos_por_id.values()
    )

    finalizados = [
        partido
        for partido in partidos_unicos
        if partido["estado"].startswith("finalizado")
    ]

    no_finalizados = [
        partido
        for partido in partidos_unicos
        if not partido["estado"].startswith("finalizado")
    ]

    print()
    print("Resumen de recolección")
    print("----------------------")
    print(
        f"Registros extraídos: {total_extraidos}"
    )
    print(
        f"Partidos únicos: {len(partidos_unicos)}"
    )
    print(
        f"Partidos finalizados: {len(finalizados)}"
    )
    print(
        f"Partidos no finalizados: {len(no_finalizados)}"
    )
    print()
    print("Guardando partidos en MongoDB...")

    resultado_mongo = guardar_partidos(
        partidos_unicos
    )

    print()
    print("Resumen de almacenamiento")
    print("-------------------------")
    print(
        f"Recibidos: {resultado_mongo['recibidos']}"
    )
    print(
        f"Insertados: {resultado_mongo['insertados']}"
    )
    print(
        f"Duplicados: {resultado_mongo['duplicados']}"
    )
    print(
        f"Inválidos: {resultado_mongo['invalidos']}"
    )
    return partidos_unicos


if __name__ == "__main__":
    recolectar_partidos_historicos()