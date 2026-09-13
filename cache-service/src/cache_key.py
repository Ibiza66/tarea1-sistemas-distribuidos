import hashlib
import json


def construir_cache_key(consulta):
    contenido = json.dumps(
        consulta,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":")
    )

    hash_consulta = hashlib.sha256(
        contenido.encode("utf-8")
    ).hexdigest()

    return f"cache:{hash_consulta}"