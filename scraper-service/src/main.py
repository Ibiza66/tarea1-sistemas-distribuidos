"""
Servicio Scraper - Tarea 1 Sistemas Distribuidos.

Este servicio será responsable de obtener y procesar información
de la Liga de Primera de Chile desde la fuente externa definida
para la tarea.

El desarrollo se realizará progresivamente. En esta primera etapa
solo se crea la API base para comprobar que el servicio puede
ejecutarse correctamente dentro de Docker.
"""

from fastapi import FastAPI


app = FastAPI(
    title="Scraper Service",
    description="Servicio encargado de obtener información de fútbol chileno.",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    """
    Permite comprobar que el servicio está disponible.

    Este endpoint será útil posteriormente para verificar desde
    Docker y desde otros servicios que el scraper está operativo.
    """

    return {
        "estado": "ok",
        "servicio": "scraper-service"
    }