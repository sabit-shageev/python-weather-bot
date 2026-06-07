# services/weather.py

import requests
from config import WEATHER_API_KEY


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
    """
    Делает запрос к OpenWeather API и возвращает красиво оформленный текст.
    """

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"

    # timeout — защита от зависания
    data = requests.get(url, timeout=5).json()

    temp = round(data["main"]["temp"])
    feels = round(data["main"]["feels_like"])
    desc = data["weather"][0]["description"]
    wind_speed = data["wind"]["speed"]
    humidity = data["main"]["humidity"]
    weather_id = data["weather"][0]["id"]

    emoji = get_weather_emoji(weather_id)

    return f"""🌍 Погода в {city}:
{emoji} {desc.capitalize()}
🌡 {temp}°C
🤔 Ощущается как: {feels}°C
🍃 Ветер: {wind_speed} м/с
💧 Влажность: {humidity}%"""


def get_weather_forecast(city):
    """
    Прогноз погоды на ближайшие 24 часа
    """

    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"

    data = requests.get(url, timeout=5).json()

    forecast_list = data["list"][:8]  # 8 * 3 часа = 24 часа

    result = f"📊 Прогноз на 24 часа в {city}:\n\n"

    for item in forecast_list:
        time = item["dt_txt"].split(" ")[1][:5]
        temp = round(item["main"]["temp"])
        desc = item["weather"][0]["description"]

        result += f"{time} — {temp}°C, {desc}\n"

    return result