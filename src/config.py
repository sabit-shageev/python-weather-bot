# config.py

# Работа с переменными окружения (.env)
import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Токен Telegram-бота
TOKEN = os.getenv("TOKEN")

# API ключ погоды
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Базовый URL Telegram API
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"

# Имя файла базы данных
DB_NAME = "src/db/users.db"

# Состояния пользователя (FSM — упрощенная)
STATE_WAITING_INFO = "waiting_for_info"
STATE_READY = "ready"