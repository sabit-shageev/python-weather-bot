import pytest
from unittest.mock import patch, MagicMock
from src.bot.telegram_api import get_updates_from_tg, send_message, send_keyboard


def test_get_updates_from_tg_success():
    """Тест: успешное получение обновлений"""
    mock_response = {"result": [{"update_id": 1, "message": {"text": "test"}}]}
    with patch('src.bot.telegram_api.requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_response
        result = get_updates_from_tg(offset=0)
        assert result == mock_response


def test_get_updates_from_tg_error():
    """Тест: ошибка при получении обновлений"""
    with patch('src.bot.telegram_api.requests.get') as mock_get:
        mock_get.side_effect = Exception("Connection error")
        result = get_updates_from_tg()
        assert result == {"result": []}


def test_send_message():
    """Тест: отправка сообщения"""
    with patch('src.bot.telegram_api.requests.post') as mock_post:
        send_message("123", "Hello")
        mock_post.assert_called_once()


def test_send_keyboard():
    """Тест: отправка клавиатуры"""
    with patch('src.bot.telegram_api.requests.post') as mock_post:
        send_keyboard("123", "Choose action")
        mock_post.assert_called_once()