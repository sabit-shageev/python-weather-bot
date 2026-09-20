import pytest
from src.services.validation import is_valid_time, is_valid_city, is_time_to_send
from unittest.mock import patch, MagicMock
from src.bot.telegram_api import get_updates_from_tg, send_message, send_keyboard

# --- Тесты для is_valid_time ---
def test_is_valid_time_correct():
    """Проверяем, что функция возвращает True для корректного времени"""
    assert is_valid_time("08:00") is True
    assert is_valid_time("23:59") is True
    assert is_valid_time("00:00") is True
    assert is_valid_time("14:30") is True


def test_is_valid_time_incorrect_format():
    """Проверяем, что функция возвращает False для неверного формата"""
    assert is_valid_time("8:00") is False      # нет ведущего нуля
    assert is_valid_time("08-00") is False     # неверный разделитель
    assert is_valid_time("08:00:00") is False  # лишние секунды
    assert is_valid_time("") is False          # пустая строка
    assert is_valid_time("abcd") is False      # не числа


def test_is_valid_time_incorrect_values():
    """Проверяем, что функция возвращает False для неверных значений времени"""
    assert is_valid_time("24:00") is False     # час вне диапазона
    assert is_valid_time("12:60") is False     # минута вне диапазона
    assert is_valid_time("99:99") is False     # оба значения вне диапазона


# --- Тесты для is_time_to_send ---
def test_is_time_to_send_true():
    """Проверяем, что функция возвращает True, когда время совпадает"""
    assert is_time_to_send("08:00", "08:00") is True


def test_is_time_to_send_false():
    """Проверяем, что функция возвращает False, когда время не совпадает"""
    assert is_time_to_send("08:00", "08:01") is False
    assert is_time_to_send("08:00", "09:00") is False

  
    
def test_is_valid_city_success():
    """Проверяем, что функция возвращает True, если город существует"""
    with patch('src.services.validation.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        assert is_valid_city("Moscow") is True


def test_is_valid_city_not_found():
    """Проверяем, что функция возвращает False, если город не найден"""
    with patch('src.services.validation.requests.get') as mock_get:
        mock_get.return_value.status_code = 404
        assert is_valid_city("NonExistentCity") is False


def test_is_valid_city_api_error():
    """Проверяем, что функция возвращает False при ошибке API"""
    with patch('src.services.validation.requests.get') as mock_get:
        mock_get.side_effect = Exception("API error")
        assert is_valid_city("Moscow") is False