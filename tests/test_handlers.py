import pytest
from unittest.mock import MagicMock, patch
from src.handlers.user_input import handle_user_input, handle_user_actions


def test_handle_user_input_success():
    """Тест: успешная обработка ввода пользователя"""
    mock_save = MagicMock()
    mock_get_user = MagicMock(return_value={"chat_id": "123", "state": "waiting_for_city"})
    mock_get_weather = MagicMock(return_value="🌤 Погода: 25°C")
    mock_send_message = MagicMock()
    mock_send_keyboard = MagicMock()
    mock_get_timezone_offset = MagicMock(return_value=10800)
    mock_is_valid_city = MagicMock(return_value=True)
    mock_is_valid_time = MagicMock(return_value=True)
    
    with patch('src.handlers.user_input.save_user_to_bd', mock_save):
        with patch('src.handlers.user_input.get_user_from_bd', mock_get_user):
            with patch('src.handlers.user_input.get_weather', mock_get_weather):
                with patch('src.handlers.user_input.send_message', mock_send_message):
                    with patch('src.handlers.user_input.send_keyboard', mock_send_keyboard):
                        with patch('src.handlers.user_input.get_timezone_offset', mock_get_timezone_offset):
                            with patch('src.handlers.user_input.is_valid_city', mock_is_valid_city):
                                with patch('src.handlers.user_input.is_valid_time', mock_is_valid_time):
                                    handle_user_input("123", "TestUser, Moscow, 08:00")
                                    
                                    mock_save.assert_called_once()
                                    mock_send_message.assert_called()
                                    mock_send_keyboard.assert_called()


def test_handle_user_input_invalid_format():
    """Тест: неверный формат ввода"""
    mock_send_message = MagicMock()
    
    with patch('src.handlers.user_input.send_message', mock_send_message):
        handle_user_input("123", "TestUser Moscow 08:00")  # без запятых
        
        mock_send_message.assert_called_with("123", "Используй формат: Имя, Город, 08:00")


def test_handle_user_input_invalid_city():
    """Тест: город не найден"""
    mock_send_message = MagicMock()
    mock_is_valid_city = MagicMock(return_value=False)
    
    with patch('src.handlers.user_input.send_message', mock_send_message):
        with patch('src.handlers.user_input.is_valid_city', mock_is_valid_city):
            handle_user_input("123", "TestUser, NonExistentCity, 08:00")
            
            mock_send_message.assert_called_with(
                "123", 
                "Город не найден\nПопробуйте еще раз\nИспользуй формат: Имя, Город, 08:00"
            )


def test_handle_user_input_invalid_time():
    """Тест: неверный формат времени"""
    mock_send_message = MagicMock()
    mock_is_valid_city = MagicMock(return_value=True)
    mock_is_valid_time = MagicMock(return_value=False)
    
    with patch('src.handlers.user_input.send_message', mock_send_message):
        with patch('src.handlers.user_input.is_valid_city', mock_is_valid_city):
            with patch('src.handlers.user_input.is_valid_time', mock_is_valid_time):
                handle_user_input("123", "TestUser, Moscow, 25:00")
                
                mock_send_message.assert_called_with("123", "Неверный формат времени")


def test_handle_user_input_exception():
    """Тест: обработка исключения"""
    mock_send_message = MagicMock()
    mock_save = MagicMock(side_effect=Exception("DB error"))
    
    with patch('src.handlers.user_input.send_message', mock_send_message):
        with patch('src.handlers.user_input.save_user_to_bd', mock_save):
            handle_user_input("123", "TestUser, Moscow, 08:00")
            
            mock_send_message.assert_called()
            # Проверяем, что сообщение об ошибке содержит текст
            call_args = mock_send_message.call_args[0]
            assert "Ошибка" in call_args[1]


def test_handle_user_actions_no_user():
    """Тест: действия без пользователя"""
    mock_get_user = MagicMock(return_value=None)
    mock_send_message = MagicMock()
    
    with patch('src.handlers.user_input.get_user_from_bd', mock_get_user):
        with patch('src.handlers.user_input.send_message', mock_send_message):
            handle_user_actions("123", "🌤 Текущая погода")
            
            mock_send_message.assert_called_with("123", "Сначала настрой бота через /start")