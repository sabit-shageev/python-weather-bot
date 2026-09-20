import pytest
from unittest.mock import MagicMock, patch
from src.handlers.start import handle_start


def test_handle_start():
    mock_save = MagicMock()
    mock_send = MagicMock()
    
    with patch('src.handlers.start.save_user_to_bd', mock_save):
        with patch('src.handlers.start.send_message', mock_send):
            handle_start("123")
            
            mock_save.assert_called_once_with("123", None, None, None, "waiting_for_info")
            mock_send.assert_called_once()