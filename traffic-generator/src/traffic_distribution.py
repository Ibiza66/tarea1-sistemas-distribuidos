"""
Distribuciones utilizadas para generar el tráfico del sistema.

Se implementan dos patrones de acceso:

- Uniforme: todos los tipos de consulta tienen la misma probabilidad.
- Zipf: unas pocas consultas concentran una mayor proporción de accesos.

Esto permitirá comparar posteriormente el efecto de ambos patrones
sobre el comportamiento de la caché.
"""

TIPOS_CONSULTA = ["Q1", "Q2", "Q3", "Q4", "Q5"]


def seleccionar_uniforme(generador_aleatorio):
    """
    Selecciona un tipo de consulta utilizando distribución uniforme.

    Todas las consultas Q1-Q5 tienen la misma probabilidad
    de ser seleccionadas.
    """

    return generador_aleatorio.choice(TIPOS_CONSULTA)


def seleccionar_zipf(generador_aleatorio, parametro_s=1.2):
    """
    Selecciona un tipo de consulta siguiendo una distribución de Zipf.

    En Zipf, las consultas con menor rango tienen una probabilidad
    mayor de ser seleccionadas. Esto permite simular escenarios donde
    unas pocas consultas concentran gran parte del tráfico.

    Parameters
    ----------
    generador_aleatorio : random.Random
        Generador aleatorio utilizado para mantener reproducibilidad.

    parametro_s : float
        Controla qué tan concentrada es la distribución.
        Valores mayores producen una mayor concentración en
        las consultas de primeros rangos.

    Returns
    -------
    str
        Tipo de consulta seleccionado.
    """

    if parametro_s <= 0:
        raise ValueError(
            "El parámetro s de Zipf debe ser mayor que cero."
        )

    # A cada consulta se le asigna un rango:
    # Q1 -> 1, Q2 -> 2, ..., Q5 -> 5.
    #
    # En una distribución Zipf, el peso de cada elemento es
    # proporcional a 1 / rango^s.
    pesos = [
        1 / (rango ** parametro_s)
        for rango in range(1, len(TIPOS_CONSULTA) + 1)
    ]

    return generador_aleatorio.choices(
        TIPOS_CONSULTA,
        weights=pesos,
        k=1
    )[0]