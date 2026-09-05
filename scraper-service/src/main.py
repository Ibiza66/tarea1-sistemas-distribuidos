"""
Servicio Scraper - Tarea 1 Sistemas Distribuidos.

Este servicio será responsable de obtener y procesar información
de la Liga de Primera de Chile desde la fuente externa definida
para la tarea.

El desarrollo se realizará progresivamente. En esta primera etapa
solo se crea la API base para comprobar que el servicio puede
ejecutarse correctamente dentro de Docker.
"""

from fastapi import FastAPI, HTTPException

from source_client import obtener_pagina_soccerway


app = FastAPI(
    title="Scraper Service",
    description="Servicio encargado de obtener información de fútbol chileno.",
    version="0.1.0"
)


@app.get("/source-health")
def source_health():
    """
    Comprueba que el scraper pueda acceder correctamente
    a la fuente externa Soccerway.
    """

    try:
        resultado = obtener_pagina_soccerway()

        return {
            "estado": "ok",
            "fuente": "Soccerway",
            "codigo_http": resultado["codigo_http"],
            "tiempo_scraping_ms": resultado["tiempo_scraping_ms"],
            "tamano_html_bytes": len(
                resultado["html"].encode("utf-8")
            )
        }

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error)
        )