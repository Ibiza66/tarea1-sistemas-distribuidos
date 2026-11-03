from datetime import datetime, timezone
from pymongo import MongoClient

from config import (
    MONGO_URI,
    MONGO_DB,
    MONGO_OUTPUT_COLLECTION
)


def guardar_resultados(resultados):

    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    try:
        client.admin.command("ping")

        db = client[MONGO_DB]
        coleccion = db[MONGO_OUTPUT_COLLECTION]

        fecha_procesamiento = datetime.now(timezone.utc)

        for nombre_consulta, datos in resultados.items():

            documento = {
                "consulta": nombre_consulta,
                "fecha_procesamiento": fecha_procesamiento,
                "cantidad_resultados": len(datos),
                "resultados": datos
            }

            coleccion.replace_one(
                {"consulta": nombre_consulta},
                documento,
                upsert=True
            )

            print(
                f"Resultados guardados: {nombre_consulta} "
                f"({len(datos)} registros)"
            )

        print(
            f"\nResultados almacenados en "
            f"{MONGO_DB}.{MONGO_OUTPUT_COLLECTION}"
        )

    finally:
        client.close()