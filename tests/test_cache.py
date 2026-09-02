"""
Тесты для модуля cache.py.
Здесь мы проверяем:
- Получение данных из кэша (есть / нет)
- Сохранение данных в кэш
- Разные TTL для погоды и прогноза
"""

from src.services.cache import get_cached_weather, set_cached_weather, get_cached_forecast, set_cached_forecast


def test_get_cached_weather_exists(mock_redis):
    """
    Проверяем, что get_cached_weather() возвращает данные,
    если они есть в Redis.
    """
    # Настраиваем мок: Redis вернул строку
    mock_redis.get.return_value = "☀️ Москва: 25°C, ясно"
    
    # Вызываем функцию
    result = get_cached_weather("Moscow")
    
    # Проверяем, что Redis был вызван с правильным ключом
    mock_redis.get.assert_called_once_with("weather:moscow")
    
    # Проверяем результат
    assert result == "☀️ Москва: 25°C, ясно"


def test_get_cached_weather_not_exists(mock_redis):
    """
    Проверяем, что get_cached_weather() возвращает None,
    если данных в Redis нет.
    """
    # Настраиваем мок: Redis вернул None
    mock_redis.get.return_value = None
    
    result = get_cached_weather("Moscow")
    
    # Проверяем, что Redis был вызван
    mock_redis.get.assert_called_once_with("weather:moscow")
    
    # Проверяем результат
    assert result is None


def test_set_cached_weather(mock_redis):
    """
    Проверяем, что set_cached_weather() сохраняет данные в Redis
    с правильным ключом, TTL и значением.
    """
    # Вызываем функцию сохранения
    set_cached_weather("Moscow", "☀️ Москва: 25°C, ясно", ttl=600)
    
    # Проверяем, что Redis.setex был вызван с правильными параметрами
    mock_redis.setex.assert_called_once_with(
        "weather:moscow",  # ключ
        600,               # TTL в секундах (10 минут)
        "☀️ Москва: 25°C, ясно"  # значение
    )


def test_get_cached_forecast_exists(mock_redis):
    """
    Проверяем, что get_cached_forecast() работает аналогично.
    """
    mock_redis.get.return_value = "Прогноз: 25°C, ясно"
    
    result = get_cached_forecast("Moscow")
    
    # Ключ для прогноза — другой префикс
    mock_redis.get.assert_called_once_with("forecast:moscow")
    assert result == "Прогноз: 25°C, ясно"


def test_set_cached_forecast(mock_redis):
    """
    Проверяем, что для прогноза используется другой TTL (1 час).
    """
    set_cached_forecast("Moscow", "Прогноз: 25°C, ясно", ttl=3600)
    
    mock_redis.setex.assert_called_once_with(
        "forecast:moscow",
        3600,  # 1 час
        "Прогноз: 25°C, ясно"
    )