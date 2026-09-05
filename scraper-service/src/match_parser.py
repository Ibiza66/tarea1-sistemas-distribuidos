"""
Procesamiento de partidos obtenidos desde Soccerway.

Este módulo transforma el HTML renderizado de Soccerway en
estructuras de datos simples que puedan ser utilizadas por
las consultas del scraper.
"""

from datetime import datetime

from bs4 import BeautifulSoup


ANIO_TEMPORADA = 2026


def normalizar_fecha_hora(texto_fecha_hora):
    """
    Convierte una fecha de Soccerway al formato estándar.

    Ejemplo:
        "05.09. 00:30"

    Se transforma en:
        fecha = "2026-09-05"
        hora = "00:30"
    """

    fecha_hora = datetime.strptime(
        f"{texto_fecha_hora} {ANIO_TEMPORADA}",
        "%d.%m. %H:%M %Y"
    )

    return (
        fecha_hora.strftime("%Y-%m-%d"),
        fecha_hora.strftime("%H:%M")
    )


def convertir_goles(elemento):
    """
    Convierte el marcador a entero.

    Si el partido todavía no tiene resultado, devuelve None.
    """

    if elemento is None:
        return None

    texto = elemento.get_text(strip=True)

    if not texto:
        return None

    try:
        return int(texto)
    except ValueError:
        return None


def normalizar_nombre_equipo(nombre):
    """
    Unifica variantes de nombres entregadas por Soccerway.
    """

    equivalencias = {
        "U. DeChile": "U. De Chile",
        "U. DeConcepción": "U. De Concepción",
        "U. LaCalera": "U. La Calera",
    }

    return equivalencias.get(nombre, nombre)


def extraer_nombre_equipo(elemento):
    """
    Obtiene el nombre del equipo.

    Se prioriza el atributo alt del escudo porque Soccerway
    mantiene ahí el nombre completo del participante.
    """

    imagen = elemento.select_one(
        '[data-testid="wcl-participantLogo"]'
    )

    if imagen and imagen.get("alt"):
        return normalizar_nombre_equipo(
            imagen["alt"].strip()
        )

    return normalizar_nombre_equipo(
        elemento.get_text(
            " ",
            strip=True
        )
    )


def extraer_partidos(html):
    """
    Extrae los partidos disponibles desde el HTML renderizado.
    """

    soup = BeautifulSoup(html, "html.parser")

    elementos_partido = soup.select("div.event__match")

    partidos = []

    for elemento in elementos_partido:
        fecha_hora_elemento = elemento.select_one(
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

        if not (
            fecha_hora_elemento
            and equipo_local
            and equipo_visitante
        ):
            continue

        texto_fecha_hora = fecha_hora_elemento.get_text(
            " ",
            strip=True
        )

        try:
            fecha, hora = normalizar_fecha_hora(
                texto_fecha_hora
            )
        except ValueError:
            continue

        partido = {
            "fecha": fecha,
            "hora": hora,
            "equipo_local": extraer_nombre_equipo(
                equipo_local
            ),
            "equipo_visitante": extraer_nombre_equipo(
                equipo_visitante
            ),
            "goles_local": convertir_goles(
                goles_local
            ),
            "goles_visitante": convertir_goles(
                goles_visitante
            )
        }

        partidos.append(partido)

    return partidos