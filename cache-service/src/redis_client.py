"""
Se encarga de la comunicación con Redis, para obtener, guardar y eliminar valores del cache."""

import redis

from config import REDIS_HOST, REDIS_PORT


cliente_redis = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)


def obtener_cache(key):
    return cliente_redis.get(key)


def guardar_cache(key, valor, ttl):
    cliente_redis.set(key, valor, ex=ttl)


def eliminar_cache(key):
    cliente_redis.delete(key)

def obtener_evictions():
    estadisticas = cliente_redis.info("stats")
    return int(estadisticas.get("evicted_keys", 0))