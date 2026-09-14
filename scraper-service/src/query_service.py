"""
Construcción de consultas sintéticas para el Generador de Tráfico.

Se generan consultas Q1 a Q5 utilizando equipos reales de la
Liga de Primera de Chile y rangos de fechas variables.
"""

from datetime import date, timedelta


EQUIPOS = [
    "Colo Colo",
    "U. Católica",
    "U. De Chile",
    "Everton",
    "Palestino",
    "Limache",
    "Ñublense",
    "Dep. Concepción",
    "La Serena",
    "Coquimbo",
    "Audax",
    "O'Higgins",
    "Huachipato",
    "Cobresal",
    "U. De Concepción",
    "U. La Calera",
]


def generar_consulta(tipo_consulta, generador_aleatorio):
    """
    Construye una consulta sintética según el tipo solicitado.
    """

    if tipo_consulta == "Q1":
        equipo = generador_aleatorio.choice(EQUIPOS)

        return {
            "tipo_consulta": "Q1",
            "parametros": {
                "equipo": equipo
            }
        }

    if tipo_consulta == "Q2":
        equipo = generador_aleatorio.choice(EQUIPOS)

        return {
            "tipo_consulta": "Q2",
            "parametros": {
                "equipo": equipo
            }
        }

    if tipo_consulta == "Q3":
        equipo_1, equipo_2 = generador_aleatorio.sample(
            EQUIPOS,
            2
        )

        # Se ordenan para evitar que A-B y B-A
        # generen dos claves distintas para la misma consulta.
        equipo_1, equipo_2 = sorted(
            [equipo_1, equipo_2]
        )

        return {
            "tipo_consulta": "Q3",
            "parametros": {
                "equipo_1": equipo_1,
                "equipo_2": equipo_2
            }
        }

    if tipo_consulta == "Q4":
        # Se generan períodos distribuidos a lo largo
        # de la temporada 2026.
        fecha_base = date(2026, 3, 1)

        dias_inicio = generador_aleatorio.randint(
            0,
            190
        )

        duracion = generador_aleatorio.randint(
            0,
            14
        )

        fecha_inicio = (
            fecha_base
            + timedelta(days=dias_inicio)
        )

        fecha_fin = (
            fecha_inicio
            + timedelta(days=duracion)
        )

        return {
            "tipo_consulta": "Q4",
            "parametros": {
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": fecha_fin.isoformat()
            }
        }

    if tipo_consulta == "Q5":
        return {
            "tipo_consulta": "Q5",
            "parametros": {}
        }

    raise ValueError(
        f"Tipo de consulta no válido: {tipo_consulta}"
    )