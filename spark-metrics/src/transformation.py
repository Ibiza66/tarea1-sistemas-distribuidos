def es_partido_valido(partido):
    """
    Comprueba si el encuentro tiene los datos necesarios
    para calcular estadísticas.
    """
    if partido.get("estado") != "finalizado":
        return False

    if not partido.get("equipo_local") or not partido.get("equipo_visitante"):
        return False

    if partido["equipo_local"] == partido["equipo_visitante"]:
        return False

    try:
        goles_local = int(partido["goles_local"])
        goles_visita = int(partido["goles_visitante"])
    except (TypeError, ValueError):
        return False

    return goles_local >= 0 and goles_visita >= 0


def generar_contribuciones(partido):

    local = partido["equipo_local"]
    visitante = partido["equipo_visitante"]

    goles_local = partido["goles_local"]
    goles_visitante = partido["goles_visitante"]

    if goles_local > goles_visitante:
        resultado_local = "Victoria"
        resultado_visitante = "Derrota"

    elif goles_local < goles_visitante:
        resultado_local = "Derrota"
        resultado_visitante = "Victoria"

    else:
        resultado_local = "Empate"
        resultado_visitante = "Empate"

    puntos = {
        "Victoria": 3,
        "Empate": 1,
        "Derrota": 0
    }

    clave_local = (
        local,
        partido["temporada"],
        partido["competicion"]
    )

    clave_visitante = (
        visitante,
        partido["temporada"],
        partido["competicion"]
    )

    contribucion_local = {
        "resultado": resultado_local,
        "goles_favor": goles_local,
        "goles_contra": goles_visitante,
        "puntos": puntos[resultado_local]
    }

    contribucion_visitante = {
        "resultado": resultado_visitante,
        "goles_favor": goles_visitante,
        "goles_contra": goles_local,
        "puntos": puntos[resultado_visitante]
    }

    return [
        (clave_local, contribucion_local),
        (clave_visitante, contribucion_visitante)
    ]