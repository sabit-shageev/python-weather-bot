# services/validation.py

import re
import requests
from datetime import datetime
from config import WEATHER_API_KEY


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
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}"
        return requests.get(url, timeout=5).status_code == 200
    except:
        return False


def is_time_to_send(user_time):
    """
    Проверяет, пора ли отправлять сообщение.
    """

    return datetime.now().strftime("%H:%M") == user_time


def already_sent_today(user):
    """
    Проверяет, отправляли ли уже сообщение сегодня.
    """

    return user["last_sent"] == datetime.now().strftime("%Y-%m-%d")