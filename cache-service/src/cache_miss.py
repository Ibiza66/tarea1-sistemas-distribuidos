"""
Módulo encargado de manejar los cache misses. Cuando no se encuentra un valor en el cache, 
este módulo se encarga de consultar al scraper-service para obtener la respuesta, guardarla en el cache
 y devolverla al cliente.
 """

import requests
import json

from config import CACHE_TTL, SCRAPER_SERVICE_URL, CACHE_TIMEOUT
from redis_client import guardar_cache


def consultar_scraper(consulta):
    """
    Consulta al scraper-service para obtener la respuesta a una consulta."""
    print(">>> Consultando scraper-service...")
    response = requests.post(
        f"{SCRAPER_SERVICE_URL}/consulta",
        json=consulta,
        timeout=CACHE_TIMEOUT
    )

    response.raise_for_status()

    respuesta = response.json()

    print(">>> Respuesta recibida desde scraper-service")

    return respuesta


def procesar_miss(consulta, key):
    """
    Procesa un cache miss. Consulta al scraper-service para obtener la respuesta, la guarda en el cache y la devuelve al cliente."""
    print(">>> CACHE MISS")

    # Consultar scraper
    respuesta = consultar_scraper(consulta)

    # Convertir respuesta a JSON
    valor = json.dumps(
        respuesta,
        ensure_ascii=False
    )

    # Guardar en Redis
    guardar_cache(
        key,
        valor,
        CACHE_TTL
    )

    print(">>> Respuesta guardada en Redis")

    return respuesta