"""
Cliente encargado de renderizar páginas dinámicas de Soccerway.

Soccerway carga parte de la información mediante JavaScript, por lo
que requests no permite acceder directamente a todos los partidos.
Playwright permite ejecutar la página como lo haría un navegador.
"""

import time

from playwright.sync_api import sync_playwright


RESULTADOS_URL = (
    "https://cl.soccerway.com/chile/liga-de-primera/resultados/"
)

LIGA_URL = (
    "https://cl.soccerway.com/chile/liga-de-primera/"
)

TABLA_URL = (
    "https://cl.soccerway.com/chile/liga-de-primera/"
    "tabla-de-posiciones/"
)


def construir_url_resultados(temporada=2026):
    """
    Construye la URL de resultados de Soccerway
    para una temporada determinada.

    Ejemplos:
        2025 -> liga-de-primera-2025
        2016/2017 -> liga-de-primera-2016-2017
    """

    temporada_texto = str(temporada)

    if temporada_texto == "2026":
        return RESULTADOS_URL

    temporada_slug = temporada_texto.replace("/", "-")

    return (
        "https://cl.soccerway.com/chile/"
        f"liga-de-primera-{temporada_slug}/resultados/"
    )


def obtener_html_resultados(
    temporada=2026,
    timeout_ms=30000
):
    """
    Renderiza la página de resultados de una temporada
    y devuelve su HTML completo.
    """

    tiempo_inicio = time.perf_counter()

    try:
        with sync_playwright() as playwright:
            navegador = playwright.chromium.launch(
                headless=True
            )

            pagina = navegador.new_page()

            pagina.goto(
                construir_url_resultados(temporada),
                wait_until="domcontentloaded",
                timeout=timeout_ms
            )

            pagina.wait_for_selector(
                "div.event__match",
                timeout=timeout_ms
            )

            html = pagina.content()

            navegador.close()

        tiempo_renderizado_ms = (
            time.perf_counter() - tiempo_inicio
        ) * 1000

        return {
            "html": html,
            "tiempo_renderizado_ms": round(
                tiempo_renderizado_ms,
                3
            )
        }

    except Exception as error:
        raise RuntimeError(
            f"Error al renderizar Soccerway: {error}"
        ) from error


def obtener_html_liga(timeout_ms=30000):
    """
    Renderiza la página principal de la Liga de Primera.

    Esta página contiene los próximos partidos necesarios
    para implementar la consulta Q1.
    """

    tiempo_inicio = time.perf_counter()

    try:
        with sync_playwright() as playwright:
            navegador = playwright.chromium.launch(
                headless=True
            )

            pagina = navegador.new_page()

            pagina.goto(
                LIGA_URL,
                wait_until="domcontentloaded",
                timeout=timeout_ms
            )

            pagina.wait_for_selector(
                "div.event__match",
                timeout=timeout_ms
            )

            html = pagina.content()

            navegador.close()

        tiempo_renderizado_ms = (
            time.perf_counter() - tiempo_inicio
        ) * 1000

        return {
            "html": html,
            "tiempo_renderizado_ms": round(
                tiempo_renderizado_ms,
                3
            )
        }

    except Exception as error:
        raise RuntimeError(
            f"Error al renderizar Soccerway: {error}"
        ) from error


def obtener_html_tabla(timeout_ms=30000):
    """
    Renderiza la tabla de posiciones de la Liga de Primera.
    """

    tiempo_inicio = time.perf_counter()

    try:
        with sync_playwright() as playwright:
            navegador = playwright.chromium.launch(
                headless=True
            )

            pagina = navegador.new_page()

            pagina.goto(
                TABLA_URL,
                wait_until="domcontentloaded",
                timeout=timeout_ms
            )

            pagina.wait_for_selector(
                "div.ui-table__row",
                timeout=timeout_ms
            )

            html = pagina.content()

            navegador.close()

        tiempo_renderizado_ms = (
            time.perf_counter() - tiempo_inicio
        ) * 1000

        return {
            "html": html,
            "tiempo_renderizado_ms": round(
                tiempo_renderizado_ms,
                3
            )
        }

    except Exception as error:
        raise RuntimeError(
            f"Error al renderizar tabla de Soccerway: {error}"
        ) from error