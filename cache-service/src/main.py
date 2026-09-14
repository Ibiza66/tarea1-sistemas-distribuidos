"""
Cache - Tarea 1 Sistemas Distribuidos.

El servicio simula un cache para almacenar resultados de consultas


"""

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Any
import json
import time

from redis_client import obtener_cache, guardar_cache, obtener_evictions
from cache_key import construir_cache_key
from config import CACHE_TTL, SCRAPER_SERVICE_URL, CACHE_TIMEOUT
from cache_miss import procesar_miss
from metrics_client import registrar_evento


app = FastAPI()


class ConsultaRequest(BaseModel):
    """
    Formato de las solicitudes recibidas desde traffic-generator."""
    tipo_consulta: str
    parametros: dict[str, Any] = Field(default_factory=dict)

@app.post("/consulta")
def recibir_consulta(consulta: ConsultaRequest):

    inicio = time.perf_counter()

    datos = consulta.model_dump()
    key = construir_cache_key(datos)

    respuesta = obtener_cache(key)

    if respuesta is not None:
        print(">>> CACHE HIT")

        latencia_ms = (
            time.perf_counter() - inicio
        ) * 1000

        registrar_evento(
            tipo_evento="hit",
            tipo_consulta=consulta.tipo_consulta,
            latencia_ms=latencia_ms
        )

        return json.loads(respuesta)

    # Cantidad de evictions antes de insertar una nueva respuesta
    evictions_antes = obtener_evictions()

    respuesta, tiempo_scraper_ms = procesar_miss(
        datos,
        key
    )

    # Cantidad de evictions después de guardar en Redis
    evictions_despues = obtener_evictions()

    nuevas_evictions = max(
        0,
        evictions_despues - evictions_antes
    )

    latencia_ms = (
        time.perf_counter() - inicio
    ) * 1000

    registrar_evento(
        tipo_evento="miss",
        tipo_consulta=consulta.tipo_consulta,
        latencia_ms=latencia_ms,
        scraping_ms=tiempo_scraper_ms,
        evictions=nuevas_evictions
    )

    return respuesta


@app.get("/test-cache")
def test_cache():
    """
    Prueba de funcionamiento del cache. Guarda un valor en el cache y luego lo obtiene."""

    key = "prueba"

    guardar_cache(
        key,
        "hola desde cache-service",
        60
    )

    valor = obtener_cache(key)

    return {
        "key": key,
        "valor": valor
    }