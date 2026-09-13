import redis
from config import REDIS_HOST, REDIS_PORT

cliente_redis = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)