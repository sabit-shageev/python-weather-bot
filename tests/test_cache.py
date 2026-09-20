import pytest
from unittest.mock import MagicMock, patch
from src.services.cache import get_cached_weather, set_cached_weather, get_cached_forecast, set_cached_forecast


def test_get_cached_weather(mock_redis_client):
    """Тест: получение погоды из кэша"""
    # Настраиваем мок-клиент, который возвращает get_redis_client()
    mock_client = MagicMock()
    mock_client.get.return_value = "☀️ 25°C"
    mock_redis_client.return_value = mock_client
    
    result = get_cached_weather("Moscow")
    
    mock_client.get.assert_called_once_with("weather:moscow")
    assert result == "☀️ 25°C"


def test_set_cached_weather(mock_redis_client):
    """Тест: сохранение погоды в кэш"""
    mock_client = MagicMock()
    mock_redis_client.return_value = mock_client
    
    set_cached_weather("Moscow", "☀️ 25°C", ttl=600)
    
    mock_client.setex.assert_called_once_with("weather:moscow", 600, "☀️ 25°C")


def test_get_cached_forecast(mock_redis_client):
    """Тест: получение прогноза из кэша"""
    mock_client = MagicMock()
    mock_client.get.return_value = "Прогноз: 25°C"
    mock_redis_client.return_value = mock_client
    
    result = get_cached_forecast("Moscow")
    
    mock_client.get.assert_called_once_with("forecast:moscow")
    assert result == "Прогноз: 25°C"


def test_set_cached_forecast(mock_redis_client):
    """Тест: сохранение прогноза в кэш"""
    mock_client = MagicMock()
    mock_redis_client.return_value = mock_client
    
    set_cached_forecast("Moscow", "Прогноз: 25°C", ttl=3600)
    
    mock_client.setex.assert_called_once_with("forecast:moscow", 3600, "Прогноз: 25°C")