"""
Generador de Tráfico - Tarea 1 Sistemas Distribuidos.

El servicio genera consultas sintéticas para simular usuarios de la
plataforma distribuida de fútbol chileno.

La configuración se obtiene mediante variables de entorno para permitir
ejecutar distintos experimentos sin modificar el código fuente.
"""

import random
import time
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
        cantidad de solicitudes, semilla, parámetro Zipf y tasa de arribo.
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

    # El intervalo entre solicitudes se obtiene a partir de la
    # tasa de arribo. Por ejemplo, 5 solicitudes/segundo
    # corresponden a un intervalo de 0.2 segundos.
    intervalo_solicitudes = 1 / configuracion["tasa_arribo"]

    print(
        f"Intervalo entre solicitudes: "
        f"{intervalo_solicitudes:.3f} segundos"
    )

    print("\nPrimeras solicitudes:")

    # Se registra el instante inicial para medir la duración
    # total de la generación de tráfico.
    tiempo_inicio = time.monotonic()

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

        # Se espera antes de generar la siguiente solicitud para
        # respetar aproximadamente la tasa de arribo configurada.
        # Después de la última solicitud no es necesario esperar.
        if numero < configuracion["cantidad_solicitudes"]:
            time.sleep(intervalo_solicitudes)

       # Se calcula cuánto demoró el proceso completo.
    tiempo_total = time.monotonic() - tiempo_inicio

    # La tasa observada se calcula utilizando la cantidad de
    # intervalos entre solicitudes. Para N solicitudes existen
    # N - 1 intervalos de llegada.
    if configuracion["cantidad_solicitudes"] > 1:
        tasa_observada = (
            (configuracion["cantidad_solicitudes"] - 1)
            / tiempo_total
        )
    else:
        tasa_observada = 0

    print(
        f"\nTiempo total: {tiempo_total:.2f} segundos"
    )

    print(
        f"Tasa observada: "
        f"{tasa_observada:.2f} solicitudes/segundo"
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