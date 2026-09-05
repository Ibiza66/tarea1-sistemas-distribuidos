"""
Cliente HTTP utilizado por el Generador de Tráfico.

Este módulo se encarga exclusivamente de la comunicación con el
servicio de caché. Mantener esta lógica separada permite modificar
o probar la comunicación sin alterar la generación de tráfico.
"""

import time

import requests


def enviar_consulta_cache(cache_url, consulta, timeout):
    """
    Envía una consulta al servicio de caché mediante HTTP POST.

    Parameters
    ----------
    cache_url : str
        Dirección base del servicio de caché.

    consulta : dict
        Consulta generada por el sistema. Contiene el tipo de
        consulta y sus parámetros.

    timeout : float
        Tiempo máximo de espera para recibir una respuesta.

    Returns
    -------
    dict
        Resultado de la comunicación, incluyendo estado,
        código HTTP, latencia, respuesta y posibles errores.
    """

    endpoint = f"{cache_url.rstrip('/')}/consulta"

    tiempo_inicio = time.perf_counter()

    try:
        respuesta = requests.post(
            endpoint,
            json=consulta,
            timeout=timeout
        )

        latencia_ms = (
            time.perf_counter() - tiempo_inicio
        ) * 1000

        # Convierte respuestas HTTP 4xx y 5xx en excepciones.
        respuesta.raise_for_status()

        try:
            datos_respuesta = respuesta.json()

        except ValueError:
            return {
                "exito": False,
                "codigo_http": respuesta.status_code,
                "latencia_ms": round(latencia_ms, 3),
                "respuesta": None,
                "error": "El servicio respondió con contenido no válido."
            }

        return {
            "exito": True,
            "codigo_http": respuesta.status_code,
            "latencia_ms": round(latencia_ms, 3),
            "respuesta": datos_respuesta,
            "error": None
        }

    except requests.exceptions.RequestException as error:

        latencia_ms = (
            time.perf_counter() - tiempo_inicio
        ) * 1000

        return {
            "exito": False,
            "codigo_http": None,
            "latencia_ms": round(latencia_ms, 3),
            "respuesta": None,
            "error": str(error)
        }