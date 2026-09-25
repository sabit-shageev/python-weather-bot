# services/validation.py

import re
from datetime import datetime, timezone, timedelta

import requests

from config import WEATHER_API_KEY, WEATHER_URL


def is_valid_time(time_str):
    """
    Проверяет формат времени HH:MM.
    """
    # Проверка через регулярное выражение
    if not re.match(r"^\d{2}:\d{2}$", time_str):
        return False

    # Проверка диапазона
    hours, minutes = map(int, time_str.split(":"))
    return 0 <= hours < 24 and 0 <= minutes < 60


def is_valid_city(city):
    """
    Проверяет, существует ли город через API.
    """
    try:
        url = f"{WEATHER_URL}?q={city}&appid={WEATHER_API_KEY}"
        return requests.get(url, timeout=5).status_code == 200
    except Exception:
        return False


def already_sent_today(user):
    """
    Проверяет, отправляли ли уже сообщение сегодня
    по локальному времени пользователя.
    """
    offset_seconds = user.get("timezone_offset", 0)
    now_utc = datetime.now(timezone.utc)
    local_now = now_utc + timedelta(seconds=offset_seconds)
    today_local = local_now.strftime("%Y-%m-%d")

    return user["last_sent"] == today_local