from pymongo import MongoClient

from config import (
    MONGO_URI,
    MONGO_DB,
    MONGO_COLLECTION
)


def cargar_partidos():

    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    try:
        # Comprobar conexión con MongoDB
        client.admin.command("ping")

        print("Conexión con MongoDB establecida.")

        db = client[MONGO_DB]

        coleccion = db[MONGO_COLLECTION]

        raw_matches = list(
            coleccion.find({}, {"_id": 0})
        )

        print(
            f"Partidos recuperados: {len(raw_matches)}"
        )

        return raw_matches

    finally:
        client.close()