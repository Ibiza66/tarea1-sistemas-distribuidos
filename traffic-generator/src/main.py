"""
Generador de Tráfico - Tarea 1 Sistemas Distribuidos.

Actualmente permite:
- Construir consultas Q1-Q5.
- Seleccionar consultas utilizando distribución Uniforme.

Posteriormente se incorporarán:
- Distribución Zipf.
- Parámetros configurables.
- Tasa de arribo.
- Envío de solicitudes al servicio de caché.
"""

import random

from query_generator import generar_consulta
from traffic_distribution import seleccionar_uniforme


def main():
    """Ejecuta una prueba del generador con distribución Uniforme."""

    print("Generador de tráfico iniciado correctamente.")

    # Una semilla fija permite reproducir la misma secuencia
    # de solicitudes al repetir el experimento.
    generador_aleatorio = random.Random(42)

    cantidad_solicitudes = 20

    print("\nConsultas generadas con distribución Uniforme:")

    for numero in range(1, cantidad_solicitudes + 1):

        tipo_consulta = seleccionar_uniforme(generador_aleatorio)

        consulta = generar_consulta(
            tipo_consulta,
            generador_aleatorio
        )

        print(f"Solicitud {numero}: {consulta}")


if __name__ == "__main__":
    main()