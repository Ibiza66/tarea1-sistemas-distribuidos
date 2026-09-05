"""
Procesamiento de la tabla de posiciones obtenida desde Soccerway.
"""

from bs4 import BeautifulSoup

from match_parser import normalizar_nombre_equipo


def extraer_tabla_posiciones(html):
    """
    Extrae la tabla completa de posiciones de la Liga de Primera.
    """

    soup = BeautifulSoup(html, "html.parser")

    filas = soup.select("div.ui-table__row")

    posiciones = []

    for fila in filas:
        celda_posicion = fila.select_one(
            ".table__cell--rank"
        )

        celda_equipo = fila.select_one(
            ".tableCellParticipant__name"
        )

        celdas_valor = fila.select(
            ".table__cell--value"
        )

        if (
            not celda_posicion
            or not celda_equipo
            or len(celdas_valor) < 7
        ):
            continue

        try:
            posicion = int(
                celda_posicion.get_text(
                    strip=True
                ).replace(".", "")
            )

            equipo = normalizar_nombre_equipo(
                celda_equipo.get_text(
                    " ",
                    strip=True
                )
            )

            partidos_jugados = int(
                celdas_valor[0].get_text(strip=True)
            )

            ganados = int(
                celdas_valor[1].get_text(strip=True)
            )

            empatados = int(
                celdas_valor[2].get_text(strip=True)
            )

            perdidos = int(
                celdas_valor[3].get_text(strip=True)
            )

            goles = celdas_valor[4].get_text(
                strip=True
            )

            goles_favor, goles_contra = map(
                int,
                goles.split(":")
            )

            diferencia_gol = int(
                celdas_valor[5].get_text(strip=True)
            )

            puntos = int(
                celdas_valor[6].get_text(strip=True)
            )

        except (ValueError, IndexError):
            continue

        posiciones.append(
            {
                "posicion": posicion,
                "equipo": equipo,
                "partidos_jugados": partidos_jugados,
                "ganados": ganados,
                "empatados": empatados,
                "perdidos": perdidos,
                "goles_favor": goles_favor,
                "goles_contra": goles_contra,
                "diferencia_gol": diferencia_gol,
                "puntos": puntos
            }
        )

    posiciones.sort(
        key=lambda equipo: equipo["posicion"]
    )

    return posiciones
