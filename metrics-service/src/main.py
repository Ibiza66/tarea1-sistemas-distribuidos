from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from threading import Lock
import time

app = FastAPI(
    title="Metrics Service",
    version="1.0.0"
)

lock = Lock()

metricas = {
    "hits": 0,
    "misses": 0,
    "errores": 0,
    "evictions": 0,
    "latencias_ms": [],
    "scraping_ms": [],
    "inicio": None,
    "ultima_solicitud": None,
}


class EventoMetrica(BaseModel):
    tipo_evento: str
    tipo_consulta: Optional[str] = None
    latencia_ms: Optional[float] = None
    scraping_ms: Optional[float] = None
    evictions: int = 0


def calcular_percentil(valores, percentil):
    if not valores:
        return 0.0

    ordenados = sorted(valores)

    posicion = (len(ordenados) - 1) * percentil
    inferior = int(posicion)
    superior = min(inferior + 1, len(ordenados) - 1)

    if inferior == superior:
        return ordenados[inferior]

    fraccion = posicion - inferior

    return (
        ordenados[inferior] * (1 - fraccion)
        + ordenados[superior] * fraccion
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "metrics-service"
    }


@app.post("/evento")
def registrar_evento(evento: EventoMetrica):

    ahora = time.time()

    with lock:
        if metricas["inicio"] is None:
            metricas["inicio"] = ahora

        metricas["ultima_solicitud"] = ahora

        tipo = evento.tipo_evento.lower()

        if tipo == "hit":
            metricas["hits"] += 1

        elif tipo == "miss":
            metricas["misses"] += 1

        elif tipo == "error":
            metricas["errores"] += 1

        if evento.evictions > 0:
            metricas["evictions"] += evento.evictions

        if evento.latencia_ms is not None:
            metricas["latencias_ms"].append(evento.latencia_ms)

        if evento.scraping_ms is not None:
            metricas["scraping_ms"].append(evento.scraping_ms)

    return {
        "status": "registrado"
    }


@app.get("/metrics")
def obtener_metricas():

    with lock:
        hits = metricas["hits"]
        misses = metricas["misses"]
        total = hits + misses

        hit_rate = hits / total if total > 0 else 0
        miss_rate = misses / total if total > 0 else 0

        latencias = metricas["latencias_ms"]
        scraping = metricas["scraping_ms"]

        if (
            metricas["inicio"] is not None
            and metricas["ultima_solicitud"] is not None
            and metricas["ultima_solicitud"] > metricas["inicio"]
        ):
            duracion = (
                metricas["ultima_solicitud"]
                - metricas["inicio"]
            )

            throughput = total / duracion

            minutos = duracion / 60
            evictions_por_minuto = (
                metricas["evictions"] / minutos
                if minutos > 0
                else 0
            )
        else:
            throughput = 0
            evictions_por_minuto = 0

        return {
            "solicitudes_totales": total,
            "hits": hits,
            "misses": misses,
            "hit_rate": round(hit_rate, 4),
            "miss_rate": round(miss_rate, 4),

            "latencia_promedio_ms": round(
                sum(latencias) / len(latencias), 3
            ) if latencias else 0,

            "latencia_p50_ms": round(
                calcular_percentil(latencias, 0.50), 3
            ),

            "latencia_p95_ms": round(
                calcular_percentil(latencias, 0.95), 3
            ),

            "scraping_promedio_ms": round(
                sum(scraping) / len(scraping), 3
            ) if scraping else 0,

            "throughput_req_s": round(throughput, 3),

            "errores": metricas["errores"],
            "evictions": metricas["evictions"],

            "evictions_por_minuto": round(
                evictions_por_minuto, 3
            )
        }


@app.post("/reset")
def reset_metricas():

    with lock:
        metricas["hits"] = 0
        metricas["misses"] = 0
        metricas["errores"] = 0
        metricas["evictions"] = 0
        metricas["latencias_ms"].clear()
        metricas["scraping_ms"].clear()
        metricas["inicio"] = None
        metricas["ultima_solicitud"] = None

    return {
        "status": "metricas reiniciadas"
    }