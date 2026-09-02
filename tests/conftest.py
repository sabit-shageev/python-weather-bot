"""
conftest.py — это специальный файл для pytest.
В нём хранятся общие настройки и фикстуры, которые используются в нескольких тестовых файлах.
Pytest автоматически подгружает фикстуры из этого файла.
"""

import pytest
from unittest.mock import patch, MagicMock

# Фикстура — это функция, которая возвращает объект для использования в тестах.
# Она выполняется перед каждым тестом (или один раз, в зависимости от скоупа).

@pytest.fixture
def mock_weather_api():
    """
    Мок для requests.get в модуле weather.py.
    Возвращает мок-объект, который мы можем настроить под нужный ответ.
    """
    # patch() заменяет реальный объект на мок во время выполнения теста
    # 'src.services.weather.requests.get' — полный путь к тому, что мы мокаем
    with patch('src.services.weather.requests.get') as mock_get:
        yield mock_get  # возвращаем мок в тест


@pytest.fixture
def mock_redis():
    """
    Мок для Redis-клиента в модуле cache.py.
    """
    with patch('src.services.cache.redis_client') as mock_redis_client:
        yield mock_redis_client


@pytest.fixture
def mock_db_connection():
    """
    Мок для подключения к БД в модуле database.py.
    Это сложный мок, потому что у нас есть вложенные объекты:
    connection → cursor → execute/fetchone/fetchall
    """
    # Создаём мок для курсора (у него есть методы execute, fetchone, fetchall)
    mock_cursor = MagicMock()
    # Создаём мок для соединения (у него есть метод cursor и commit)
    mock_conn = MagicMock()
    # Настраиваем, чтобы conn.cursor() возвращал наш мок-курсор
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    # Мокаем функцию get_connection() в database.py
    with patch('src.db.database.get_connection', return_value=mock_conn) as mock_get_conn:
        # Возвращаем и соединение, и курсор, чтобы тест мог проверить вызовы
        yield mock_conn, mock_cursor