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

def obtener_html_resultados(timeout_ms=30000):
    """
    Renderiza la página de resultados y devuelve su HTML completo.

    Returns
    -------
    dict
        HTML renderizado y tiempo utilizado para obtenerlo.

    Raises
    ------
    RuntimeError
        Si no es posible cargar correctamente la página.
    """

    tiempo_inicio = time.perf_counter()

    try:
        with sync_playwright() as playwright:
            navegador = playwright.chromium.launch(headless=True)
            pagina = navegador.new_page()

            pagina.goto(
                RESULTADOS_URL,
                wait_until="domcontentloaded",
                timeout=timeout_ms
            )

            # Esperamos hasta que Soccerway haya generado al menos
            # un partido en el DOM.
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