"""
Cache - Tarea 1 Sistemas Distribuidos.

El servicio simula un cache para almacenar resultados de consultas


"""

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Any
import json

from redis_client import obtener_cache, guardar_cache
from cache_key import construir_cache_key
from config import CACHE_TTL, SCRAPER_SERVICE_URL, CACHE_TIMEOUT
from cache_miss import procesar_miss


app = FastAPI()


class ConsultaRequest(BaseModel):
    """
    Formato de las solicitudes recibidas desde traffic-generator."""
    tipo_consulta: str
    parametros: dict[str, Any] = Field(default_factory=dict)

@app.post("/consulta")
def recibir_consulta(consulta: ConsultaRequest):
    """
    Recibe una consulta y la procesa, intentando obtenerla del cache.
    Si se tiene guardada la consulta con su respectiva clave, devuelve la respuesta directamente. Si no, la envía al scraper-service
    para obtener la respuesta, guardarla en el cache y luego devolverla.
    """

    datos = consulta.model_dump()
    key = construir_cache_key(datos)

    respuesta = obtener_cache(key)

    if respuesta is not None:
        print(">>> CACHE HIT")
        return json.loads(respuesta)

    return procesar_miss(datos, key)

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