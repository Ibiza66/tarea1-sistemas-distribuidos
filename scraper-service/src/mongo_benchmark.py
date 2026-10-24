"""
Experimentos de rendimiento de MongoDB.

Mide el tiempo de escritura masiva del dataset completo
sin modificar la colección original raw_matches.

Los resultados se guardan automáticamente en archivos
CSV y JSON para su posterior análisis.
"""

import csv
import json
import os
import time
from pathlib import Path
from statistics import mean

from pymongo import MongoClient


MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://mongodb:27017"
)

MONGO_DB = os.getenv(
    "MONGO_DB",
    "futbol_chileno"
)

EXPERIMENTS_DIR = Path(
    os.getenv(
        "EXPERIMENTS_DIR",
        "/results/tarea2"
    )
)

REPETICIONES = 3


def obtener_base_datos():
    """
    Obtiene una conexión a la base de datos.
    """

    cliente = MongoClient(MONGO_URI)

    return cliente[MONGO_DB]


def guardar_resultados_csv(resultados):
    """
    Guarda las repeticiones del experimento en CSV.
    """

    EXPERIMENTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    ruta = (
        EXPERIMENTS_DIR
        / "mongo_escritura.csv"
    )

    with ruta.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as archivo:
        campos = [
            "repeticion",
            "documentos",
            "tiempo_total_ms",
            "tiempo_por_documento_ms"
        ]

        escritor = csv.DictWriter(
            archivo,
            fieldnames=campos
        )

        escritor.writeheader()
        escritor.writerows(resultados)

    return ruta


def guardar_resumen_json(resumen):
    """
    Guarda el resumen del experimento en JSON.
    """

    EXPERIMENTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    ruta = (
        EXPERIMENTS_DIR
        / "mongo_escritura_resumen.json"
    )

    with ruta.open(
        "w",
        encoding="utf-8"
    ) as archivo:
        json.dump(
            resumen,
            archivo,
            ensure_ascii=False,
            indent=4
        )

    return ruta


def medir_escritura():
    """
    Mide tres veces la escritura del dataset completo.

    Se utiliza una colección temporal independiente
    para no modificar raw_matches.
    """

    db = obtener_base_datos()

    origen = db["raw_matches"]

    # Esta lectura ocurre antes de iniciar el cronómetro,
    # para medir solamente la operación de escritura.
    documentos = list(
        origen.find({}, {"_id": 0})
    )

    cantidad_documentos = len(
        documentos
    )

    if cantidad_documentos == 0:
        raise RuntimeError(
            "La colección raw_matches está vacía."
        )

    print(
        f"Documentos del dataset: "
        f"{cantidad_documentos}"
    )

    tiempos_ms = []
    resultados = []

    for repeticion in range(
        1,
        REPETICIONES + 1
    ):
        nombre_coleccion = (
            f"benchmark_write_{repeticion}"
        )

        destino = db[nombre_coleccion]

        destino.drop()

        # El índice existe durante la inserción,
        # por lo que su mantenimiento forma parte
        # del comportamiento medido.
        destino.create_index(
            "match_id",
            unique=True
        )

        inicio = time.perf_counter()

        resultado = destino.insert_many(
            documentos,
            ordered=False
        )

        fin = time.perf_counter()

        insertados = len(
            resultado.inserted_ids
        )

        tiempo_total_ms = (
            fin - inicio
        ) * 1000

        tiempo_documento_ms = (
            tiempo_total_ms
            / insertados
        )

        tiempos_ms.append(
            tiempo_total_ms
        )

        resultados.append({
            "repeticion": repeticion,
            "documentos": insertados,
            "tiempo_total_ms": round(
                tiempo_total_ms,
                6
            ),
            "tiempo_por_documento_ms": round(
                tiempo_documento_ms,
                9
            )
        })

        print()
        print(
            f"Repetición {repeticion}"
        )
        print(
            f"Insertados: {insertados}"
        )
        print(
            f"Tiempo total: "
            f"{tiempo_total_ms:.3f} ms"
        )
        print(
            f"Tiempo por documento: "
            f"{tiempo_documento_ms:.6f} ms"
        )

        destino.drop()

    promedio_total = mean(
        tiempos_ms
    )

    promedio_por_documento = (
        promedio_total
        / cantidad_documentos
    )

    resumen = {
        "experimento": "escritura_mongodb",
        "repeticiones": REPETICIONES,
        "documentos": cantidad_documentos,
        "tiempo_promedio_total_ms": round(
            promedio_total,
            6
        ),
        "tiempo_promedio_por_documento_ms": round(
            promedio_por_documento,
            9
        )
    }

    ruta_csv = guardar_resultados_csv(
        resultados
    )

    ruta_json = guardar_resumen_json(
        resumen
    )

    print()
    print("Resumen escritura MongoDB")
    print("-------------------------")
    print(
        f"Repeticiones: {REPETICIONES}"
    )
    print(
        f"Documentos: {cantidad_documentos}"
    )
    print(
        f"Tiempo promedio total: "
        f"{promedio_total:.3f} ms"
    )
    print(
        f"Tiempo promedio por documento: "
        f"{promedio_por_documento:.6f} ms"
    )

    print()
    print("Resultados guardados en:")
    print(ruta_csv)
    print(ruta_json)


if __name__ == "__main__":
    medir_escritura()