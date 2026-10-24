"""
Procesamiento de partidos obtenidos desde Soccerway.

Este módulo transforma el HTML renderizado de Soccerway en
estructuras de datos simples que puedan ser utilizadas por
los distintos componentes del sistema.
"""

from datetime import datetime
import re

from bs4 import BeautifulSoup


def obtener_anio_partido(temporada, texto_fecha_hora):
    """
    Determina el año correspondiente a la fecha de un partido.
    """

    temporada_texto = str(temporada).replace("-", "/")

    if "/" not in temporada_texto:
        return int(temporada_texto)

    anio_inicio, anio_fin = temporada_texto.split("/")

    partes_fecha = texto_fecha_hora.split(".")

    if len(partes_fecha) < 2:
        raise ValueError(
            f"No se pudo determinar el mes de: {texto_fecha_hora}"
        )

    mes = int(partes_fecha[1])

    if mes >= 7:
        return int(anio_inicio)

    return int(anio_fin)


def normalizar_fecha_hora(
    texto_fecha_hora,
    temporada=2026
):
    """
    Convierte las fechas entregadas por Soccerway
    a un formato estándar.

    Soporta ejemplos como:
        07.12.2025
        23.11.2025 Tras pen.
        05.09. 00:30
    """

    texto = " ".join(
        texto_fecha_hora.split()
    )

    coincidencia_fecha = re.search(
        r"\d{2}\.\d{2}\.\d{4}",
        texto
    )

    if coincidencia_fecha:
        fecha_texto = coincidencia_fecha.group()

        fecha_hora = datetime.strptime(
            fecha_texto,
            "%d.%m.%Y"
        )

        return (
            fecha_hora.strftime("%Y-%m-%d"),
            ""
        )

    anio = obtener_anio_partido(
        temporada,
        texto
    )

    formatos_sin_anio = [
        "%d.%m. %H:%M %Y",
        "%d.%m. %Y",
    ]

    for formato in formatos_sin_anio:
        try:
            fecha_hora = datetime.strptime(
                f"{texto} {anio}",
                formato
            )

            hora = (
                fecha_hora.strftime("%H:%M")
                if "%H:%M" in formato
                else ""
            )

            return (
                fecha_hora.strftime("%Y-%m-%d"),
                hora
            )

        except ValueError:
            pass

    raise ValueError(
        f"Formato de fecha no reconocido: {texto_fecha_hora}"
    )


def convertir_goles(elemento):
    """
    Obtiene los goles principales del marcador.

    Ejemplos:
        "3" -> 3
        "2(4)" -> 2

    El valor entre paréntesis corresponde a penales
    y no forma parte del marcador principal.
    """

    if elemento is None:
        return None

    texto = elemento.get_text(
        "",
        strip=True
    )

    coincidencia = re.match(
        r"\d+",
        texto
    )

    if not coincidencia:
        return None

    return int(coincidencia.group())


def extraer_penales(elemento):
    """
    Obtiene el resultado de una tanda de penales.

    Ejemplo:
        "2(4)" -> 4

    Si no existen penales, devuelve None.
    """

    if elemento is None:
        return None

    texto = elemento.get_text(
        "",
        strip=True
    )

    coincidencia = re.search(
        r"\((\d+)\)",
        texto
    )

    if not coincidencia:
        return None

    return int(coincidencia.group(1))


def normalizar_nombre_equipo(nombre):
    """
    Corrige variaciones de espaciado en nombres
    entregados por Soccerway.
    """

    nombre = nombre.strip()

    nombre = re.sub(
        r"^U\.\s*",
        "U. ",
        nombre
    )

    nombre = re.sub(
        r"\bDe(?=[A-ZÁÉÍÓÚÑ])",
        "De ",
        nombre
    )

    nombre = re.sub(
        r"\bLa(?=[A-ZÁÉÍÓÚÑ])",
        "La ",
        nombre
    )

    return nombre


def extraer_nombre_equipo(elemento):
    """
    Obtiene el nombre del equipo.
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


def extraer_match_id(elemento):
    """
    Obtiene el identificador único del partido
    entregado por Soccerway.
    """

    identificador = elemento.get("id", "")

    if identificador.startswith("g_1_"):
        return identificador.replace(
            "g_1_",
            "",
            1
        )

    enlace = elemento.select_one(
        "a.eventRowLink"
    )

    if enlace and enlace.get("href"):
        coincidencia = re.search(
            r"[?&]mid=([^&]+)",
            enlace["href"]
        )

        if coincidencia:
            return coincidencia.group(1)

    return None


def determinar_estado(
    texto_fecha_hora,
    goles_local,
    goles_visitante
):
    """
    Determina el estado general de un encuentro.
    """

    texto = texto_fecha_hora.lower()

    if "tras pen" in texto:
        return "finalizado_tras_penales"

    if "suspend" in texto:
        return "suspendido"

    if "aplaz" in texto or "reprogram" in texto:
        return "reprogramado"

    if "cancel" in texto:
        return "cancelado"

    if (
        goles_local is not None
        and goles_visitante is not None
    ):
        return "finalizado"

    return "programado"


def extraer_partidos(
    html,
    temporada=2026,
    competicion="Liga de Primera"
):
    """
    Extrae los partidos disponibles desde el HTML renderizado.
    """

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    elementos_partido = soup.select(
        "div.event__match"
    )

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

        goles_local_elemento = elemento.select_one(
            '.event__score[data-side="home"]'
        )

        goles_visitante_elemento = elemento.select_one(
            '.event__score[data-side="away"]'
        )

        if not (
            fecha_hora_elemento
            and equipo_local
            and equipo_visitante
        ):
            continue

        texto_fecha_hora = (
            fecha_hora_elemento.get_text(
                " ",
                strip=True
            )
        )

        try:
            fecha, hora = normalizar_fecha_hora(
                texto_fecha_hora,
                temporada
            )

        except (ValueError, TypeError):
            continue

        goles_local = convertir_goles(
            goles_local_elemento
        )

        goles_visitante = convertir_goles(
            goles_visitante_elemento
        )

        partido = {
            "match_id": extraer_match_id(
                elemento
            ),
            "fecha": fecha,
            "hora": hora,
            "temporada": str(temporada),
            "competicion": competicion,
            "equipo_local": extraer_nombre_equipo(
                equipo_local
            ),
            "equipo_visitante": extraer_nombre_equipo(
                equipo_visitante
            ),
            "goles_local": goles_local,
            "goles_visitante": goles_visitante,
            "penales_local": extraer_penales(
                goles_local_elemento
            ),
            "penales_visitante": extraer_penales(
                goles_visitante_elemento
            ),
            "estado": determinar_estado(
                texto_fecha_hora,
                goles_local,
                goles_visitante
            )
        }

        partidos.append(partido)

    return partidos