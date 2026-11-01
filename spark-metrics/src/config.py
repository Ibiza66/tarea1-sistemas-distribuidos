import os

# MongoDB
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://mongodb:27017"
)

MONGO_DB = os.getenv(
    "MONGO_DB",
    "futbol_chileno"
)

MONGO_COLLECTION = os.getenv(
    "COLECCION_PARTIDOS",
    "raw_matches"
)

MONGO_OUTPUT_COLLECTION = os.getenv(
    "MONGO_OUTPUT_COLLECTION",
    "estadisticas"
)

# Spark
SPARK_APP_NAME = "AnalisisEncuentros"

SPARK_MASTER = os.getenv(
    "SPARK_MASTER",
    "local[*]"
)

NUM_PARTITIONS = 1