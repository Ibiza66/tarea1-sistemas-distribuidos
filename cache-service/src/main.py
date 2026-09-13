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
    tipo_consulta: str
    parametros: dict[str, Any] = Field(default_factory=dict)

@app.post("/consulta")
def recibir_consulta(consulta: ConsultaRequest):

    datos = consulta.model_dump()
    key = construir_cache_key(datos)

    respuesta = obtener_cache(key)

    if respuesta is not None:
        print(">>> CACHE HIT")
        return json.loads(respuesta)

    return procesar_miss(datos, key)

@app.get("/test-cache")
def test_cache():

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