import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_weather_api():
    with patch('src.services.weather.requests.get') as mock_get:
        yield mock_get


@pytest.fixture
def mock_db_connection():
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.__enter__.return_value = mock_conn
    
    with patch('src.db.database.get_connection', return_value=mock_conn):
        yield mock_conn, mock_cursor


@pytest.fixture
def mock_redis_client():
    """Мок для Redis клиента (подменяем функцию get_redis_client)"""
    with patch('src.services.cache.get_redis_client') as mock_get_redis:
        mock_client = MagicMock()
        mock_client.get.return_value = None
        mock_client.setex.return_value = None
        mock_get_redis.return_value = mock_client
        yield mock_get_redis