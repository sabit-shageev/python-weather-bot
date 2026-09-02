import requests
from config import WEATHER_API_KEY
from services.cache import (
    get_cached_weather, set_cached_weather,
    get_cached_forecast, set_cached_forecast
)
from src.logger import setup_logger

logger = setup_logger("weather")


def get_weather_emoji(weather_id):
    """
    Возвращает эмодзи по коду погоды.
    """

    if 200 <= weather_id < 300:
        return "⛈"
    elif 300 <= weather_id < 400:
        return "🌦"
    elif 500 <= weather_id < 600:
        return "🌧"
    elif 600 <= weather_id < 700:
        return "❄️"
    elif 700 <= weather_id < 800:
        return "🌫"
    elif weather_id == 800:
        return "☀️"
    else:
        return "☁️"


def get_weather(city):
    # 1. Пробуем взять из кэша
    cached = get_cached_weather(city)
    if cached:
        logger.debug(f"📦 Кэш для {city}")  # опционально для лога
        return cached
    else:
        logger.debug(f"🌍 Запрос в API для {city}")

    # 2. Запрос к API
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    try:
        data = requests.get(url, timeout=5).json()
    except Exception as e:
        return f"⚠️ Ошибка при запросе погоды: {e}"

    if data.get("cod") != 200:
        return f"❌ Город {city} не найден."

    temp = round(data["main"]["temp"])
    feels = round(data["main"]["feels_like"])
    desc = data["weather"][0]["description"]
    wind_speed = data["wind"]["speed"]
    humidity = data["main"]["humidity"]
    weather_id = data["weather"][0]["id"]
    emoji = get_weather_emoji(weather_id)

    result = f"""🌍 Погода в {city}:
{emoji} {desc.capitalize()}
🌡 {temp}°C
🤔 Ощущается как: {feels}°C
🍃 Ветер: {wind_speed} м/с
💧 Влажность: {humidity}%"""

    # 3. Сохраняем в кэш на 10 минут
    set_cached_weather(city, result)
    logger.debug(f"💾 Сохранено в кэш: {city}")
    return result


def get_weather_forecast(city):
    # Кэш для прогноза
    cached = get_cached_forecast(city)
    if cached:
        logger.debug(f"📦 Кэш прогноза для {city}")
        return cached

    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    try:
        data = requests.get(url, timeout=5).json()
    except Exception as e:
        return f"⚠️ Ошибка при запросе прогноза: {e}"

    if data.get("cod") != "200":
        return f"❌ Не удалось получить прогноз для {city}."

    forecast_list = data["list"][:8]
    result = f"📊 Прогноз на 24 часа в {city}:\n\n"
    for item in forecast_list:
        time = item["dt_txt"].split(" ")[1][:5]
        temp = round(item["main"]["temp"])
        desc = item["weather"][0]["description"]
        result += f"{time} — {temp}°C, {desc}\n"

    # Кэшируем прогноз на час (погода меняется не так быстро)
    set_cached_forecast(city, result)
    return result

def get_timezone_offset(city: str) -> int:
    """
    Возвращает смещение часового пояса города от UTC в секундах.
    Использует API прогноза (/forecast), потому что в нём есть поле timezone.
    
    Аргументы:
        city (str): Название города
        
    Возвращает:
        int: Смещение в секундах (например, 10800 для Москвы, UTC+3).
             Если не удалось определить — возвращает 0 (UTC).
    """
    try:
        # Формируем URL для API прогноза (не текущей погоды)
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric"
        
        # Отправляем запрос
        response = requests.get(url, timeout=5)
        data = response.json()
        
        # В ответе прогноза есть поле city.timezone
        if data.get("city") and "timezone" in data["city"]:
            return data["city"]["timezone"]  # возвращаем смещение в секундах
        
        # Если поле timezone отсутствует — возвращаем 0 (UTC)
        return 0
        
    except Exception as e:
        # Если произошла ошибка (нет интернета, город не найден и т.д.)
        # логируем и возвращаем 0 (UTC)
        logger.warning(f"Не удалось определить часовой пояс для {city}: {e}")
        return 0