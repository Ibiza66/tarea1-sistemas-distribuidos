EQUIVALENCIAS = {
    "colo colo": "Colo-Colo",
    "colo-colo": "Colo-Colo",
    "u. de chile": "Universidad de Chile",
    "universidad de chile": "Universidad de Chile",
    "u. católica": "Universidad Católica",
    "universidad católica": "Universidad Católica"
}


def normalizar_nombre(nombre):

    nombre = nombre.strip().casefold()

    return EQUIVALENCIAS.get(
        nombre,
        nombre.title()
    )


def partido_valido(partido):

    campos_obligatorios = [
        "match_id",
        "fecha",
        "temporada",
        "competicion",
        "equipo_local",
        "equipo_visitante",
        "goles_local",
        "goles_visitante",
        "estado"
    ]

    if not all(
        partido.get(campo) is not None
        for campo in campos_obligatorios
    ):
        return False

    estados_validos = {
        "finalizado",
        "finalizado_tras_penales"
    }

    estado = str(
        partido["estado"]
    ).strip().casefold()

    if estado not in estados_validos:
        return False

    if estado == "finalizado_tras_penales":

        penales_local = partido.get("penales_local")
        penales_visitante = partido.get("penales_visitante")

        if type(penales_local) is not int:
            return False

        if type(penales_visitante) is not int:
            return False

        if penales_local < 0 or penales_visitante < 0:
            return False

        if penales_local == penales_visitante:
            return False

    if type(partido["goles_local"]) is not int:
        return False
    if type(partido["goles_visitante"]) is not int:
        return False

    if partido["goles_local"] < 0 or partido["goles_visitante"] < 0:
        return False

    if not isinstance(partido["equipo_local"], str):
        return False

    if not isinstance(partido["equipo_visitante"], str):
        return False

    if not partido["equipo_local"].strip():
        return False

    if not partido["equipo_visitante"].strip():
        return False

    local = normalizar_nombre(
        partido["equipo_local"]
    )

    visitante = normalizar_nombre(
        partido["equipo_visitante"]
    )

    if local == visitante:
        return False

    return True


def normalizar_partido(partido):

    partido_normalizado = partido.copy()

    partido_normalizado["equipo_local"] = normalizar_nombre(
        partido["equipo_local"]
    )

    partido_normalizado["equipo_visitante"] = normalizar_nombre(
        partido["equipo_visitante"]
    )

    partido_normalizado["temporada"] = str(
        partido["temporada"]
    ).strip()

    partido_normalizado["competicion"] = str(
        partido["competicion"]
    ).strip()

    return partido_normalizado