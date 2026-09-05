"""
Distribuciones utilizadas para generar el tráfico del sistema.

En esta etapa se implementa la distribución Uniforme.
Posteriormente se incorporará la distribución de Zipf.
"""

TIPOS_CONSULTA = ["Q1", "Q2", "Q3", "Q4", "Q5"]


def seleccionar_uniforme(generador_aleatorio):
    """
    Selecciona un tipo de consulta con distribución uniforme.

    Todas las consultas Q1-Q5 tienen la misma probabilidad
    de ser seleccionadas.

    Parameters
    ----------
    generador_aleatorio : random.Random
        Generador aleatorio utilizado para mantener la
        reproducibilidad de los experimentos.

    Returns
    -------
    str
        Tipo de consulta seleccionado.
    """

    return generador_aleatorio.choice(TIPOS_CONSULTA)