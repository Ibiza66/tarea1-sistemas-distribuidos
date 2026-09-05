"""
Configuración del Generador de Tráfico.

Los parámetros se obtienen desde variables de entorno para que los
experimentos puedan modificarse sin cambiar el código fuente.
"""

import os


def obtener_configuracion():
    """
    Obtiene y valida la configuración del generador.

    Returns
    -------
    dict
        Parámetros utilizados durante la generación de tráfico.
    """

    distribucion = os.getenv(
        "TRAFICO_DISTRIBUCION",
        "uniforme"
    ).lower()

    cantidad_solicitudes = int(
        os.getenv("TRAFICO_SOLICITUDES", "1000")
    )

    semilla = int(
        os.getenv("TRAFICO_SEMILLA", "42")
    )

    parametro_zipf = float(
        os.getenv("TRAFICO_ZIPF_S", "1.2")
    )

    tasa_arribo = float(
        os.getenv("TRAFICO_TASA_ARRIBO", "10")
    )

    tipos_consulta = [
        tipo.strip().upper()
        for tipo in os.getenv(
            "TRAFICO_TIPOS_CONSULTA",
            "Q1,Q2,Q3,Q4,Q5"
        ).split(",")
        if tipo.strip()
    ]

    cache_url = os.getenv(
        "CACHE_SERVICE_URL",
        "http://cache-service:8000"
    )

    cache_timeout = float(
        os.getenv("CACHE_TIMEOUT", "5")
    )

    # Tipos de consulta permitidos por el sistema.
    tipos_validos = {"Q1", "Q2", "Q3", "Q4", "Q5"}

    if distribucion not in ["uniforme", "zipf"]:
        raise ValueError(
            "TRAFICO_DISTRIBUCION debe ser 'uniforme' o 'zipf'."
        )

    if cantidad_solicitudes <= 0:
        raise ValueError(
            "TRAFICO_SOLICITUDES debe ser mayor que cero."
        )

    if parametro_zipf <= 0:
        raise ValueError(
            "TRAFICO_ZIPF_S debe ser mayor que cero."
        )

    if tasa_arribo <= 0:
        raise ValueError(
            "TRAFICO_TASA_ARRIBO debe ser mayor que cero."
        )

    if not tipos_consulta:
        raise ValueError(
            "Debe existir al menos un tipo de consulta habilitado."
        )

    if not set(tipos_consulta).issubset(tipos_validos):
        raise ValueError(
            "TRAFICO_TIPOS_CONSULTA solo puede contener "
            "Q1, Q2, Q3, Q4 y Q5."
        )

    if cache_timeout <= 0:
        raise ValueError(
            "CACHE_TIMEOUT debe ser mayor que cero."
        )

    return {
        "distribucion": distribucion,
        "cantidad_solicitudes": cantidad_solicitudes,
        "semilla": semilla,
        "parametro_zipf": parametro_zipf,
        "tasa_arribo": tasa_arribo,
        "tipos_consulta": tipos_consulta,
        "cache_url": cache_url,
        "cache_timeout": cache_timeout,
    }