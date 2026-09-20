"""
Тесты для модуля weather.py.
Здесь мы проверяем:
- Формирование правильного сообщения при успешном запросе
- Обработку ошибок (город не найден, сетевые ошибки)
- Получение часового пояса
- Формирование прогноза
"""

import pytest
from src.services.weather import get_weather, get_weather_forecast, get_timezone_offset


# -------- ТЕСТЫ ДЛЯ get_weather() --------

def test_get_weather_success(mock_weather_api):
    """
    Проверяем, что get_weather() возвращает правильное сообщение
    при успешном ответе от API.
    """
    # 1. Подготавливаем данные: создаём JSON, который вернёт API
    mock_response_data = {
        "main": {
            "temp": 22.5,      # температура
            "feels_like": 20.0,  # ощущается как
            "humidity": 65     # влажность
        },
        "weather": [
            {"id": 800, "description": "ясно"}  # код и описание погоды
        ],
        "wind": {"speed": 3.5}  # скорость ветра
    }
    
    # 2. Настраиваем мок: при вызове requests.get() вернуть объект с нужными методами
    mock_weather_api.return_value.json.return_value = mock_response_data
    mock_weather_api.return_value.status_code = 200
    
    # 3. Вызываем тестируемую функцию
    result = get_weather("Moscow")
    
    # 4. Проверяем, что результат содержит ожидаемые элементы
    # Это не точное сравнение строки, а проверка наличия ключевых фрагментов
    assert "🌍 Погода в Moscow" in result  # заголовок
    assert "☀️" in result                   # эмодзи для ясной погоды
    assert "22°C" in result                 # температура
    assert "20°C" in result                 # ощущается как
    assert "3.5 м/с" in result              # ветер
    assert "65%" in result                  # влажность
    
    # 5. Проверяем, что API был вызван ровно 1 раз с правильным URL
    mock_weather_api.assert_called_once()
    call_args = mock_weather_api.call_args[0][0]  # первый аргумент — URL
    assert "q=Moscow" in call_args


def test_get_weather_city_not_found(mock_weather_api):
    """
    Проверяем, что при вводе несуществующего города
    возвращается понятное сообщение об ошибке.
    """
    # Мокаем ответ с ошибкой 404
    mock_weather_api.return_value.json.return_value = {"cod": "404", "message": "city not found"}
    mock_weather_api.return_value.status_code = 404
    
    result = get_weather("NonExistentCity")
    
    # Проверяем, что в ответе есть сообщение об ошибке
    assert "❌ Город NonExistentCity не найден" in result


def test_get_weather_api_error(mock_weather_api):
    """
    Проверяем, что при сетевой ошибке (нет интернета, таймаут и т.д.)
    функция возвращает сообщение об ошибке, а не падает.
    """
    # Мокаем исключение: requests.get() выбрасывает ошибку
    mock_weather_api.side_effect = Exception("Network error")
    
    result = get_weather("Moscow")
    
    # Проверяем, что ошибка обработана
    assert "⚠️ Ошибка при запросе погоды" in result


# -------- ТЕСТЫ ДЛЯ get_timezone_offset() --------

def test_get_timezone_offset_success(mock_weather_api):
    """
    Проверяем, что функция правильно получает смещение часового пояса
    из ответа API прогноза.
    """
    # У API прогноза есть поле city.timezone со смещением в секундах
    mock_response = {
        "city": {
            "timezone": 10800  # 10800 секунд = 3 часа (Москва, UTC+3)
        }
    }
    mock_weather_api.return_value.json.return_value = mock_response
    mock_weather_api.return_value.status_code = 200
    
    offset = get_timezone_offset("Moscow")
    
    # Проверяем, что вернулось правильное смещение
    assert offset == 10800


def test_get_timezone_offset_fallback(mock_weather_api):
    """
    Проверяем, что если API не вернул timezone (старый формат или ошибка),
    функция возвращает 0 (UTC).
    """
    mock_response = {
        "city": {}  # пустой объект — нет timezone
    }
    mock_weather_api.return_value.json.return_value = mock_response
    mock_weather_api.return_value.status_code = 200
    
    offset = get_timezone_offset("Unknown")
    
    # Должен вернуть 0 (базовое значение)
    assert offset == 0


# -------- ТЕСТЫ ДЛЯ get_weather_forecast() --------

def test_get_weather_forecast_success(mock_weather_api):
    """
    Проверяем, что прогноз формируется правильно.
    Прогноз должен содержать 8 точек (24 часа с шагом 3 часа)
    с временем, температурой и описанием.
    """
    # Формируем ответ API — 8 элементов в списке (24 часа)
    mock_response = {
        "list": [
            {"dt_txt": "2026-08-29 06:00:00", "main": {"temp": 18.0}, "weather": [{"description": "облачно"}]},
            {"dt_txt": "2026-08-29 09:00:00", "main": {"temp": 21.0}, "weather": [{"description": "ясно"}]},
            {"dt_txt": "2026-08-29 12:00:00", "main": {"temp": 24.0}, "weather": [{"description": "солнечно"}]},
            {"dt_txt": "2026-08-29 15:00:00", "main": {"temp": 22.0}, "weather": [{"description": "облачно"}]},
            {"dt_txt": "2026-08-29 18:00:00", "main": {"temp": 19.0}, "weather": [{"description": "дождь"}]},
            {"dt_txt": "2026-08-29 21:00:00", "main": {"temp": 16.0}, "weather": [{"description": "туман"}]},
            {"dt_txt": "2026-08-30 00:00:00", "main": {"temp": 14.0}, "weather": [{"description": "ясно"}]},
            {"dt_txt": "2026-08-30 03:00:00", "main": {"temp": 13.0}, "weather": [{"description": "ясно"}]}
        ]
    }
    mock_weather_api.return_value.json.return_value = mock_response
    mock_weather_api.return_value.status_code = 200
    
    result = get_weather_forecast("Moscow")
    
    # Проверяем заголовок
    assert "📊 Прогноз на 24 часа в Moscow" in result
    
    # Проверяем, что все 8 точек прогноза есть в результате
    assert "06:00 — 18°C, облачно" in result
    assert "09:00 — 21°C, ясно" in result
    assert "12:00 — 24°C, солнечно" in result
    assert "15:00 — 22°C, облачно" in result
    assert "18:00 — 19°C, дождь" in result
    assert "21:00 — 16°C, туман" in result
    assert "00:00 — 14°C, ясно" in result
    assert "03:00 — 13°C, ясно" in result