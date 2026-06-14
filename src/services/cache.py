import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_cached_weather(city: str):
    key = f"weather:{city.lower()}"
    return redis_client.get(key)

def set_cached_weather(city: str, text: str, ttl: int = 600):
    key = f"weather:{city.lower()}"
    redis_client.setex(key, ttl, text)

def get_cached_forecast(city: str):
    key = f"forecast:{city.lower()}"
    return redis_client.get(key)

def set_cached_forecast(city: str, text: str, ttl: int = 3600):
    key = f"forecast:{city.lower()}"
    redis_client.setex(key, ttl, text)