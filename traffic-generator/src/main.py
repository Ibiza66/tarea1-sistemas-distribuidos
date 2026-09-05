"""
Generador de Tráfico - Tarea 1 Sistemas Distribuidos.

Este servicio simulará solicitudes realizadas por usuarios hacia
la plataforma distribuida de fútbol chileno.

El desarrollo se realizará progresivamente:

1. Construcción de consultas Q1-Q5.
2. Distribución Uniforme.
3. Distribución Zipf.
4. Tasa de arribo configurable.
5. Envío de solicitudes al servicio de caché.
"""

import random

from query_generator import generar_consulta


def main():
    """Ejecuta una prueba inicial del generador de consultas."""

    print("Generador de tráfico iniciado correctamente.")

    # La semilla permite obtener los mismos resultados
    # al repetir un experimento con la misma configuración.
    generador_aleatorio = random.Random(42)

    tipos_consulta = ["Q1", "Q2", "Q3", "Q4", "Q5"]

    print("\nConsultas de prueba:")

    for tipo in tipos_consulta:
        consulta = generar_consulta(
            tipo,
            generador_aleatorio
        )

        print(consulta)


if __name__ == "__main__":
    main()