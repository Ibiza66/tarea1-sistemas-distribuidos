"""
Distribuciones utilizadas para generar el tráfico del sistema.

Se implementan dos patrones de acceso:

- Uniforme: todos los tipos habilitados tienen la misma probabilidad.
- Zipf: las consultas de menor rango concentran una mayor proporción
  de los accesos.
"""


def seleccionar_uniforme(generador_aleatorio, tipos_consulta):
    """
    Selecciona uniformemente entre los tipos de consulta habilitados.
    """

    return generador_aleatorio.choice(tipos_consulta)


def seleccionar_zipf(
    generador_aleatorio,
    tipos_consulta,
    parametro_s=1.2
):
    """
    Selecciona un tipo de consulta utilizando una distribución Zipf.

    El peso de cada consulta es proporcional a 1 / rango^s.
    """

    if parametro_s <= 0:
        raise ValueError(
            "El parámetro s de Zipf debe ser mayor que cero."
        )

    pesos = [
        1 / (rango ** parametro_s)
        for rango in range(1, len(tipos_consulta) + 1)
    ]

    return generador_aleatorio.choices(
        tipos_consulta,
        weights=pesos,
        k=1
    )[0]