"""
Construcción de consultas sintéticas para el Generador de Tráfico.

Cada consulta utiliza una estructura común para facilitar su envío
posterior al servicio de caché.

Tipos de consulta:
Q1: próximos partidos de un equipo.
Q2: últimos partidos de un equipo.
Q3: historial entre dos equipos.
Q4: partidos dentro de un período.
Q5: tabla completa de posiciones.
"""

import random
from datetime import date, timedelta


# Lista inicial utilizada para probar el generador.
# Más adelante podrá reemplazarse o ampliarse mediante configuración.
EQUIPOS = [
    "Colo-Colo",
    "Universidad de Chile",
    "Universidad Católica",
]


def generar_consulta(tipo_consulta, generador_aleatorio):
    """
    Construye una consulta sintética según el tipo solicitado.

    Parameters
    ----------
    tipo_consulta : str
        Identificador de la consulta: Q1, Q2, Q3, Q4 o Q5.

    generador_aleatorio : random.Random
        Generador aleatorio utilizado para hacer reproducibles
        los experimentos mediante una semilla.

    Returns
    -------
    dict
        Consulta estructurada con su tipo y parámetros.
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
        equipo_1, equipo_2 = generador_aleatorio.sample(EQUIPOS, 2)

        return {
            "tipo_consulta": "Q3",
            "parametros": {
                "equipo_1": equipo_1,
                "equipo_2": equipo_2
            }
        }

    if tipo_consulta == "Q4":
        # Se utiliza una fecha fija para mantener reproducibilidad
        # entre distintas ejecuciones del experimento.
        fecha_inicio = date(2026, 9, 1)

        dias_extra = generador_aleatorio.randint(0, 7)
        fecha_fin = fecha_inicio + timedelta(days=dias_extra)

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