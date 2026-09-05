"""
Funciones para obtener identificadores de la competición
desde el HTML de Soccerway.
"""

import re


def extraer_identificadores_competicion(html):
    """
    Extrae los identificadores principales de la Liga de Primera
    desde la configuración incluida por Soccerway en el HTML.
    """

    patron_template = r'"tournament_id":"([^"]+)"'
    patron_torneo = r'"tournamentId":"([^"]+)"'

    template_match = re.search(patron_template, html)
    torneo_match = re.search(patron_torneo, html)

    if not template_match or not torneo_match:
        raise ValueError(
            "No fue posible encontrar los identificadores "
            "de la competición en Soccerway."
        )

    return {
        "tournament_template_id": template_match.group(1),
        "tournament_id": torneo_match.group(1)
    }
