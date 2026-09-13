import requests

from config import METRICS_SERVICE_URL, METRICS_TIMEOUT


def registrar_evento(
    tipo_evento,
    tipo_consulta=None,
    latencia_ms=None,
    scraping_ms=None,
    evictions=0
):
    payload = {
        "tipo_evento": tipo_evento,
        "tipo_consulta": tipo_consulta,
        "latencia_ms": latencia_ms,
        "scraping_ms": scraping_ms,
        "evictions": evictions
    }

    try:
        response = requests.post(
            f"{METRICS_SERVICE_URL}/evento",
            json=payload,
            timeout=METRICS_TIMEOUT
        )

        response.raise_for_status()

    except requests.RequestException as error:
        print(
            f">>> No fue posible registrar métrica: {error}"
        )