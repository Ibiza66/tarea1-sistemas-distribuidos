"""
Generador de Tráfico - Tarea 1 Sistemas Distribuidos.

Actualmente permite:
- Construir consultas Q1-Q5.
- Seleccionar consultas mediante distribución Uniforme.
- Seleccionar consultas mediante distribución de Zipf.
- Repetir experimentos utilizando una semilla fija.

Posteriormente se incorporarán:
- Configuración mediante variables de entorno.
- Tasa de arribo configurable.
- Envío de solicitudes al servicio de caché.
"""

import random
from collections import Counter

from query_generator import generar_consulta
from traffic_distribution import seleccionar_uniforme, seleccionar_zipf


def probar_distribucion(nombre, cantidad_solicitudes=1000, semilla=42):
    """
    Genera solicitudes de prueba y cuenta cuántas veces aparece
    cada tipo de consulta.

    Esta función permite verificar experimentalmente el comportamiento
    de las distribuciones Uniforme y Zipf antes de enviar tráfico real
    al servicio de caché.
    """

    generador_aleatorio = random.Random(semilla)
    conteo = Counter()

    print(f"\nDistribución: {nombre}")

    for numero in range(1, cantidad_solicitudes + 1):

        if nombre == "uniforme":
            tipo_consulta = seleccionar_uniforme(
                generador_aleatorio
            )

        elif nombre == "zipf":
            tipo_consulta = seleccionar_zipf(
                generador_aleatorio,
                parametro_s=1.2
            )

        else:
            raise ValueError(
                f"Distribución no válida: {nombre}"
            )

        consulta = generar_consulta(
            tipo_consulta,
            generador_aleatorio
        )

        conteo[consulta["tipo_consulta"]] += 1

        # Solo mostramos las primeras cinco solicitudes para
        # evitar imprimir cientos de líneas en la terminal.
        if numero <= 5:
            print(
                f"Solicitud {numero}: {consulta}"
            )

    print("\nResumen:")

    for tipo in ["Q1", "Q2", "Q3", "Q4", "Q5"]:

        cantidad = conteo[tipo]

        porcentaje = (
            cantidad / cantidad_solicitudes
        ) * 100

        print(
            f"{tipo}: {cantidad} solicitudes "
            f"({porcentaje:.2f}%)"
        )


def main():
    """Ejecuta pruebas iniciales de ambas distribuciones."""

    print("Generador de tráfico iniciado correctamente.")

    probar_distribucion(
        nombre="uniforme"
    )

    probar_distribucion(
        nombre="zipf"
    )


if __name__ == "__main__":
    main()