"""
Servicio Scraper - Tarea 1 Sistemas Distribuidos.

El servicio obtiene información de la Liga de Primera desde
Soccerway, la procesa y la mantiene en memoria para responder
las consultas Q1 a Q5.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from match_parser import extraer_partidos
from query_service import (
    obtener_enfrentamientos,
    obtener_partidos_periodo,
    obtener_proximos_partidos,
    obtener_ultimos_partidos,
)
from render_client import (
    obtener_html_liga,
    obtener_html_resultados,
    obtener_html_tabla,
)
from source_client import obtener_pagina_soccerway
from standings_parser import extraer_tabla_posiciones


# Datos precargados que utilizarán las consultas.
DATOS = {
    "resultados": [],
    "liga": [],
    "tabla": [],
    "tiempos_carga_ms": {},
    "cargado": False,
    "error_carga": None,
}


class ConsultaRequest(BaseModel):
    """
    Formato de las solicitudes recibidas desde cache-service.
    """

    tipo_consulta: str
    parametros: dict[str, Any] = Field(
        default_factory=dict
    )


def cargar_datos():
    """
    Obtiene y procesa la información necesaria desde Soccerway.

    La carga se realiza una vez al iniciar el servicio para evitar
    ejecutar scraping completo en cada consulta.
    """

    try:
        resultados_render = obtener_html_resultados()
        liga_render = obtener_html_liga()
        tabla_render = obtener_html_tabla()

        DATOS["resultados"] = extraer_partidos(
            resultados_render["html"]
        )

        DATOS["liga"] = extraer_partidos(
            liga_render["html"]
        )

        DATOS["tabla"] = extraer_tabla_posiciones(
            tabla_render["html"]
        )

        DATOS["tiempos_carga_ms"] = {
            "resultados": resultados_render[
                "tiempo_renderizado_ms"
            ],
            "liga": liga_render[
                "tiempo_renderizado_ms"
            ],
            "tabla": tabla_render[
                "tiempo_renderizado_ms"
            ],
        }

        DATOS["cargado"] = True
        DATOS["error_carga"] = None

    except Exception as error:
        DATOS["cargado"] = False
        DATOS["error_carga"] = str(error)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Precarga los datos al iniciar FastAPI.

    asyncio.to_thread permite ejecutar Playwright fuera del
    event loop principal de FastAPI.
    """

    await asyncio.to_thread(cargar_datos)

    yield


app = FastAPI(
    title="Scraper Service",
    description=(
        "Servicio encargado de obtener información "
        "de fútbol chileno desde Soccerway."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    """
    Comprueba el estado general del scraper.
    """

    return {
        "estado": (
            "ok"
            if DATOS["cargado"]
            else "degradado"
        ),
        "servicio": "scraper-service",
        "datos_cargados": DATOS["cargado"],
        "error_carga": DATOS["error_carga"],
        "cantidad_resultados": len(
            DATOS["resultados"]
        ),
        "cantidad_partidos_liga": len(
            DATOS["liga"]
        ),
        "cantidad_equipos_tabla": len(
            DATOS["tabla"]
        ),
    }


@app.get("/source-health")
def source_health():
    """
    Comprueba que Soccerway esté accesible.
    """

    try:
        resultado = obtener_pagina_soccerway()

        return {
            "estado": "ok",
            "fuente": "Soccerway",
            "codigo_http": resultado[
                "codigo_http"
            ],
            "tiempo_scraping_ms": resultado[
                "tiempo_scraping_ms"
            ],
            "tamano_html_bytes": len(
                resultado["html"].encode("utf-8")
            ),
        }

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error


def obtener_parametro(
    parametros,
    nombre
):
    """
    Obtiene y valida un parámetro obligatorio.
    """

    valor = parametros.get(nombre)

    if not isinstance(valor, str) or not valor.strip():
        raise HTTPException(
            status_code=400,
            detail=f"Falta el parámetro '{nombre}'.",
        )

    return valor.strip()


@app.post("/consulta")
def realizar_consulta(consulta: ConsultaRequest):
    """
    Procesa las consultas Q1 a Q5 solicitadas por cache-service.
    """

    if not DATOS["cargado"]:
        raise HTTPException(
            status_code=503,
            detail=(
                "Los datos del scraper no están disponibles. "
                f"Error: {DATOS['error_carga']}"
            ),
        )

    tipo = consulta.tipo_consulta.upper()
    parametros = consulta.parametros

    try:
        if tipo == "Q1":
            equipo = obtener_parametro(
                parametros,
                "equipo"
            )

            datos = obtener_proximos_partidos(
                DATOS["liga"],
                equipo
            )

        elif tipo == "Q2":
            equipo = obtener_parametro(
                parametros,
                "equipo"
            )

            datos = obtener_ultimos_partidos(
                DATOS["resultados"],
                equipo
            )

        elif tipo == "Q3":
            equipo_1 = obtener_parametro(
                parametros,
                "equipo_1"
            )

            equipo_2 = obtener_parametro(
                parametros,
                "equipo_2"
            )

            datos = obtener_enfrentamientos(
                DATOS["resultados"],
                equipo_1,
                equipo_2
            )

        elif tipo == "Q4":
            fecha_inicio = obtener_parametro(
                parametros,
                "fecha_inicio"
            )

            fecha_fin = obtener_parametro(
                parametros,
                "fecha_fin"
            )

            datos = obtener_partidos_periodo(
                DATOS["resultados"],
                fecha_inicio,
                fecha_fin
            )

        elif tipo == "Q5":
            datos = DATOS["tabla"]

        else:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Tipo de consulta inválido. "
                    "Debe ser Q1, Q2, Q3, Q4 o Q5."
                ),
            )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return {
        "tipo_consulta": tipo,
        "cantidad": len(datos),
        "datos": datos,
    }