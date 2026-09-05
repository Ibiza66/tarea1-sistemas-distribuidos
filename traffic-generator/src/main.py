"""
Generador de Tráfico - Tarea 1 Sistemas Distribuidos.

El servicio genera consultas sintéticas para simular usuarios de la
plataforma distribuida de fútbol chileno.

La configuración se obtiene mediante variables de entorno para permitir
ejecutar distintos experimentos sin modificar el código fuente.
"""

import random
from collections import Counter

from config import obtener_configuracion
from query_generator import generar_consulta
from traffic_distribution import seleccionar_uniforme, seleccionar_zipf


def ejecutar_generador(configuracion):
    """
    Genera solicitudes utilizando la configuración entregada.

    Parameters
    ----------
    configuracion : dict
        Parámetros del experimento, incluyendo distribución,
        cantidad de solicitudes, semilla y parámetro Zipf.
    """

    generador_aleatorio = random.Random(
        configuracion["semilla"]
    )

    conteo = Counter()

    print("Generador de tráfico iniciado correctamente.")
    print("\nConfiguración:")
    print(f"Distribución: {configuracion['distribucion']}")
    print(
        f"Cantidad de solicitudes: "
        f"{configuracion['cantidad_solicitudes']}"
    )
    print(f"Semilla: {configuracion['semilla']}")

    if configuracion["distribucion"] == "zipf":
        print(
            f"Parámetro Zipf s: "
            f"{configuracion['parametro_zipf']}"
        )

    print(
        f"Tasa de arribo configurada: "
        f"{configuracion['tasa_arribo']} solicitudes/segundo"
    )

    print("\nPrimeras solicitudes:")

    for numero in range(
        1,
        configuracion["cantidad_solicitudes"] + 1
    ):

        if configuracion["distribucion"] == "uniforme":
            tipo_consulta = seleccionar_uniforme(
                generador_aleatorio
            )

        else:
            tipo_consulta = seleccionar_zipf(
                generador_aleatorio,
                configuracion["parametro_zipf"]
            )

        consulta = generar_consulta(
            tipo_consulta,
            generador_aleatorio
        )

        conteo[consulta["tipo_consulta"]] += 1

        # Solo se muestran las primeras cinco solicitudes para
        # mantener una salida de terminal fácil de revisar.
        if numero <= 5:
            print(
                f"Solicitud {numero}: {consulta}"
            )

    print("\nResumen:")

    for tipo in ["Q1", "Q2", "Q3", "Q4", "Q5"]:

        cantidad = conteo[tipo]

        porcentaje = (
            cantidad /
            configuracion["cantidad_solicitudes"]
        ) * 100

        print(
            f"{tipo}: {cantidad} solicitudes "
            f"({porcentaje:.2f}%)"
        )


def main():
    """Obtiene la configuración e inicia el generador."""

    configuracion = obtener_configuracion()

    ejecutar_generador(configuracion)


if __name__ == "__main__":
    main()