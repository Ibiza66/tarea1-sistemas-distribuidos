"""
Cliente para acceder a la fuente externa Soccerway.

Este módulo concentra la comunicación HTTP con la fuente externa.
Separar esta responsabilidad permite manejar timeouts, errores de
conexión y respuestas inválidas sin mezclar esta lógica con el
procesamiento de los datos.
"""

import time

import requests


SOCCERWAY_URL = "https://cl.soccerway.com/chile/liga-de-primera/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


def obtener_pagina_soccerway(timeout=10):
    """
    Obtiene el contenido HTML de la Liga de Primera desde Soccerway.

    Parameters
    ----------
    timeout : float
        Tiempo máximo de espera para la respuesta de la fuente externa.

    Returns
    -------
    dict
        Resultado de la solicitud, incluyendo contenido HTML,
        código HTTP y tiempo empleado.

    Raises
    ------
    RuntimeError
        Si Soccerway no responde correctamente.
    """

    tiempo_inicio = time.perf_counter()

    try:
        respuesta = requests.get(
            SOCCERWAY_URL,
            headers=HEADERS,
            timeout=timeout
        )

        tiempo_scraping_ms = (
            time.perf_counter() - tiempo_inicio
        ) * 1000

        respuesta.raise_for_status()

        if not respuesta.text.strip():
            raise RuntimeError(
                "Soccerway respondió sin contenido."
            )

        return {
            "html": respuesta.text,
            "codigo_http": respuesta.status_code,
            "tiempo_scraping_ms": round(
                tiempo_scraping_ms,
                3
            )
        }

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Error al acceder a Soccerway: {error}"
        ) from error
    