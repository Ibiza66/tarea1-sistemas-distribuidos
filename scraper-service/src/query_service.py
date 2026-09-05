"""
Funciones de consulta sobre los datos obtenidos desde Soccerway.

Este módulo implementa las consultas solicitadas por el sistema
sin depender directamente del proceso de scraping.
"""

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

    Parameters
    ----------
    partidos : list
        Partidos procesados desde Soccerway.

    equipo : str
        Nombre del equipo solicitado.

    cantidad : int
        Número máximo de partidos a devolver.

    Returns
    -------
    list
        Últimos partidos del equipo.
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