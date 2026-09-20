import redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

_redis_client = None

def get_redis_client():
    """Возвращает клиент Redis (создаёт при первом вызове)"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    return _redis_client


def get_cached_weather(city: str):
    key = f"weather:{city.lower()}"
    return get_redis_client().get(key)


def set_cached_weather(city: str, text: str, ttl: int = 600):
    key = f"weather:{city.lower()}"
    get_redis_client().setex(key, ttl, text)


def get_cached_forecast(city: str):
    key = f"forecast:{city.lower()}"
    return get_redis_client().get(key)


def set_cached_forecast(city: str, text: str, ttl: int = 3600):
    key = f"forecast:{city.lower()}"
    get_redis_client().setex(key, ttl, text)