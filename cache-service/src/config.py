import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

CACHE_TTL = int(os.getenv("CACHE_TTL", "60"))

SCRAPER_SERVICE_URL = os.getenv(
    "SCRAPER_SERVICE_URL",
    "http://scraper-service:8001"
)

CACHE_TIMEOUT = float(os.getenv("CACHE_TIMEOUT", "5"))