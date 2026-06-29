# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# ---------- TELEGRAM ----------
BOT_TOKEN = os.getenv("TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не задан в .env")

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ---------- WEATHER API ----------
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
if not WEATHER_API_KEY:
    raise ValueError("❌ WEATHER_API_KEY не задан в .env")

# ---------- POSTGRESQL ----------
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "weatherbot"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", ""),
}

# ---------- REDIS ----------
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Состояния пользователя (FSM — упрощенная)
STATE_WAITING_INFO = "waiting_for_info"
STATE_READY = "ready"


# ---------- ЛОГИ (опционально) ----------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")