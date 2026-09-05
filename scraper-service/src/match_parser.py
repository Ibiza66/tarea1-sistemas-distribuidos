"""
Procesamiento de partidos obtenidos desde Soccerway.

Este módulo transforma el HTML renderizado de Soccerway en
estructuras de datos simples que puedan ser utilizadas por
las consultas del scraper.
"""

from bs4 import BeautifulSoup


def extraer_partidos(html):
    """
    Extrae los partidos disponibles desde el HTML renderizado.

    Parameters
    ----------
    html : str
        HTML generado después de ejecutar JavaScript en Soccerway.

    Returns
    -------
    list
        Lista de diccionarios con la información de cada partido.
    """

    soup = BeautifulSoup(html, "html.parser")

    elementos_partido = soup.select("div.event__match")

    partidos = []

    for elemento in elementos_partido:
        fecha_hora = elemento.select_one(
            '[data-testid="wcl-stageTime"]'
        )

        equipo_local = elemento.select_one(
            ".event__homeParticipant"
        )

        equipo_visitante = elemento.select_one(
            ".event__awayParticipant"
        )

        goles_local = elemento.select_one(
            '.event__score[data-side="home"]'
        )

        goles_visitante = elemento.select_one(
            '.event__score[data-side="away"]'
        )

        # Ignoramos bloques incompletos que no contienen
        # los datos mínimos necesarios de un partido.
        if not (
            fecha_hora
            and equipo_local
            and equipo_visitante
        ):
            continue

        partido = {
            "fecha_hora": fecha_hora.get_text(
                " ",
                strip=True
            ),
            "equipo_local": equipo_local.get_text(
                " ",
                strip=True
            ),
            "equipo_visitante": equipo_visitante.get_text(
                " ",
                strip=True
            ),
            "goles_local": (
                goles_local.get_text(strip=True)
                if goles_local
                else None
            ),
            "goles_visitante": (
                goles_visitante.get_text(strip=True)
                if goles_visitante
                else None
            )
        }

        partidos.append(partido)

    return partidos