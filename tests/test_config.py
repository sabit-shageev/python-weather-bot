import os
import pytest
from src import config


def test_config_variables_exist():
    """Проверяем, что основные переменные конфигурации определены"""
    assert hasattr(config, 'TOKEN')
    assert hasattr(config, 'WEATHER_API_KEY')
    assert hasattr(config, 'TELEGRAM_URL')
    assert hasattr(config, 'STATE_READY')


def test_telegram_url_format():
    """Проверяем, что URL для Telegram формируется корректно"""
    # Так как TOKEN может быть не задан в тестовой среде, мы проверяем только структуру
    assert config.TELEGRAM_URL.startswith("https://api.telegram.org/bot")