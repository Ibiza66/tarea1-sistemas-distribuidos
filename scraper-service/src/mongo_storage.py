"""
Funciones de almacenamiento persistente en MongoDB.

Los partidos recolectados desde Soccerway se almacenan
en la colección raw_matches utilizando match_id como
identificador único para evitar duplicados.
"""

import os

from pymongo import MongoClient
from pymongo.errors import BulkWriteError


MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://mongodb:27017"
)

MONGO_DB = os.getenv(
    "MONGO_DB",
    "futbol_chileno"
)

COLECCION_PARTIDOS = "raw_matches"


def obtener_coleccion_partidos():
    """
    Obtiene la colección donde se almacenan
    los partidos recolectados.
    """

    cliente = MongoClient(MONGO_URI)

    base_datos = cliente[MONGO_DB]

    coleccion = base_datos[
        COLECCION_PARTIDOS
    ]

    return coleccion


def preparar_coleccion():
    """
    Crea un índice único sobre match_id.

    Esto impide almacenar dos veces el mismo partido
    aunque el scraper se ejecute repetidamente.
    """

    coleccion = obtener_coleccion_partidos()

    coleccion.create_index(
        "match_id",
        unique=True
    )


def guardar_partidos(partidos):
    """
    Guarda una lista de partidos en MongoDB.

    Devuelve estadísticas de inserción,
    duplicados y registros inválidos.
    """

    coleccion = obtener_coleccion_partidos()

    preparar_coleccion()

    validos = []
    invalidos = 0

    for partido in partidos:
        if not partido.get("match_id"):
            invalidos += 1
            continue

        validos.append(partido)

    if not validos:
        return {
            "recibidos": len(partidos),
            "insertados": 0,
            "duplicados": 0,
            "invalidos": invalidos
        }

    try:
        resultado = coleccion.insert_many(
            validos,
            ordered=False
        )

        insertados = len(
            resultado.inserted_ids
        )

        duplicados = 0

    except BulkWriteError as error:
        detalles = error.details

        insertados = detalles.get(
            "nInserted",
            0
        )

        errores = detalles.get(
            "writeErrors",
            []
        )

        duplicados = sum(
            1
            for item in errores
            if item.get("code") == 11000
        )

    return {
        "recibidos": len(partidos),
        "insertados": insertados,
        "duplicados": duplicados,
        "invalidos": invalidos
    }