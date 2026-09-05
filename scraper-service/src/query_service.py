"""
Funciones de consulta sobre los datos obtenidos desde Soccerway.

Este módulo implementa las consultas solicitadas por el sistema
sin depender directamente del proceso de scraping.
"""

from datetime import date
import re
import unicodedata


ALIAS_EQUIPOS = {
    "colo colo": "Colo Colo",
    "universidad de chile": "U. De Chile",
    "u de chile": "U. De Chile",
    "universidad catolica": "U. Católica",
    "u catolica": "U. Católica",
}


def normalizar_texto(texto):
    """
    Normaliza nombres para facilitar comparaciones.

    Ejemplo:
        "Colo-Colo" -> "colo colo"
        "U. Católica" -> "u catolica"
    """

    texto = unicodedata.normalize("NFD", texto)

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    texto = texto.lower()

    texto = re.sub(r"[^a-z0-9]+", " ", texto)

    return texto.strip()


def resolver_nombre_equipo(equipo):
    """
    Convierte nombres conocidos al formato utilizado por Soccerway.
    """

    nombre_normalizado = normalizar_texto(equipo)

    return ALIAS_EQUIPOS.get(
        nombre_normalizado,
        equipo
    )


def obtener_ultimos_partidos(partidos, equipo, cantidad=5):
    """
    Obtiene los últimos partidos finalizados de un equipo.
    """

    equipo_resuelto = resolver_nombre_equipo(equipo)

    equipo_normalizado = normalizar_texto(
        equipo_resuelto
    )

    encontrados = []

    for partido in partidos:
        local = normalizar_texto(
            partido["equipo_local"]
        )

        visitante = normalizar_texto(
            partido["equipo_visitante"]
        )

        pertenece_equipo = (
            local == equipo_normalizado
            or visitante == equipo_normalizado
        )

        partido_finalizado = (
            partido["goles_local"] is not None
            and partido["goles_visitante"] is not None
        )

        if pertenece_equipo and partido_finalizado:
            encontrados.append(
                {
                    "fecha": partido["fecha"],
                    "equipo_local": partido["equipo_local"],
                    "equipo_visitante": partido["equipo_visitante"],
                    "resultado": (
                        f"{partido['goles_local']}-"
                        f"{partido['goles_visitante']}"
                    )
                }
            )

    encontrados.sort(
        key=lambda partido: partido["fecha"],
        reverse=True
    )

    return encontrados[:cantidad]


def obtener_enfrentamientos(
    partidos,
    equipo_1,
    equipo_2
):
    """
    Obtiene los enfrentamientos finalizados entre dos equipos.
    """

    equipo_1_resuelto = resolver_nombre_equipo(
        equipo_1
    )

    equipo_2_resuelto = resolver_nombre_equipo(
        equipo_2
    )

    equipo_1_normalizado = normalizar_texto(
        equipo_1_resuelto
    )

    equipo_2_normalizado = normalizar_texto(
        equipo_2_resuelto
    )

    enfrentamientos = []

    for partido in partidos:
        local = normalizar_texto(
            partido["equipo_local"]
        )

        visitante = normalizar_texto(
            partido["equipo_visitante"]
        )

        mismos_equipos = (
            (
                local == equipo_1_normalizado
                and visitante == equipo_2_normalizado
            )
            or
            (
                local == equipo_2_normalizado
                and visitante == equipo_1_normalizado
            )
        )

        partido_finalizado = (
            partido["goles_local"] is not None
            and partido["goles_visitante"] is not None
        )

        if mismos_equipos and partido_finalizado:
            enfrentamientos.append(
                {
                    "fecha": partido["fecha"],
                    "equipo_local": partido["equipo_local"],
                    "equipo_visitante": partido["equipo_visitante"],
                    "resultado": (
                        f"{partido['goles_local']}-"
                        f"{partido['goles_visitante']}"
                    )
                }
            )

    enfrentamientos.sort(
        key=lambda partido: partido["fecha"],
        reverse=True
    )

    return enfrentamientos


def obtener_partidos_periodo(
    partidos,
    fecha_inicio,
    fecha_fin
):
    """
    Obtiene partidos dentro de un período de fechas.
    """

    try:
        inicio = date.fromisoformat(fecha_inicio)
        fin = date.fromisoformat(fecha_fin)
    except ValueError as error:
        raise ValueError(
            "Las fechas deben tener formato YYYY-MM-DD."
        ) from error

    if inicio > fin:
        raise ValueError(
            "La fecha de inicio no puede ser posterior "
            "a la fecha de término."
        )

    encontrados = []

    for partido in partidos:
        fecha_partido = date.fromisoformat(
            partido["fecha"]
        )

        if inicio <= fecha_partido <= fin:
            if (
                partido["goles_local"] is not None
                and partido["goles_visitante"] is not None
            ):
                resultado = (
                    f"{partido['goles_local']}-"
                    f"{partido['goles_visitante']}"
                )
            else:
                resultado = None

            encontrados.append(
                {
                    "fecha": partido["fecha"],
                    "hora": partido["hora"],
                    "equipo_local": partido["equipo_local"],
                    "equipo_visitante": partido["equipo_visitante"],
                    "resultado": resultado
                }
            )

    encontrados.sort(
        key=lambda partido: (
            partido["fecha"],
            partido["hora"]
        )
    )

    return encontrados