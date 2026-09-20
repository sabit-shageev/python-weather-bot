"""
Тесты для обработчиков команд.
Здесь мы проверяем, что команды правильно обрабатывают ввод пользователя.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.handlers.user_input import handle_user_input


@patch('src.handlers.user_input.get_weather')
@patch('src.handlers.user_input.get_user_from_bd')
@patch('src.handlers.user_input.save_user_to_bd')
def test_handle_city_input_saves_city(mock_save, mock_get_user, mock_get_weather, mock_bot):
    """
    Проверяем, что когда пользователь вводит город, он сохраняется в БД.
    """
    # Настраиваем моки
    mock_get_user.return_value = {"chat_id": "123", "state": "waiting_for_city"}
    mock_get_weather.return_value = "🌤 Погода: 25°C"
    
    # Создаём мок сообщения
    message = MagicMock()
    message.text = "Moscow"
    message.from_user.id = "123"
    message.from_user.first_name = "TestUser"
    
    # Создаём мок бота
    bot = MagicMock()
    
    # Вызываем функцию
    handle_city_input(message, bot)
    
    # Проверяем, что город сохранился в БД
    mock_save.assert_called_with("123", "TestUser", "Moscow", None, "ready")
    
    # Проверяем, что бот отправил сообщение с погодой
    bot.send_message.assert_called()