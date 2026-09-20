"""
Тесты для модуля database.py.
Здесь мы проверяем:
- Создание таблиц
- Сохранение пользователя
- Получение пользователя по ID
- Получение всех пользователей
- Обновление даты последней отправки
"""

import pytest
from unittest.mock import MagicMock
from src.db.database import init_db, save_user_to_bd, get_user_from_bd, get_all_users_from_bd, update_last_sent


def test_init_db(mock_db_connection):
    """
    Проверяем, что init_db() выполняет правильный SQL-запрос.
    """
    # Распаковываем моки из фикстуры
    mock_conn, mock_cursor = mock_db_connection
    
    # Вызываем тестируемую функцию
    init_db()
    
    # Проверяем, что курсор выполнил CREATE TABLE с нужным запросом
    # Важно: в запросе должно быть все поля, включая timezone_offset
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args[0][0]  # первый аргумент — SQL-запрос
    assert "CREATE TABLE IF NOT EXISTS users" in call_args
    assert "timezone_offset INTEGER DEFAULT 0" in call_args
    
    # Проверяем, что транзакция была подтверждена (commit)
    mock_conn.commit.assert_called_once()


def test_save_user_to_bd(mock_db_connection):
    """
    Проверяем, что save_user_to_bd() выполняет INSERT с правильными данными.
    """
    mock_conn, mock_cursor = mock_db_connection
    
    # Вызываем функцию сохранения
    save_user_to_bd("123", "TestUser", "Moscow", "08:00", "ready", last_sent=None, timezone_offset=10800)
    
    # Проверяем, что execute был вызван с правильными аргументами
    mock_cursor.execute.assert_called_once()
    # Проверяем SQL-запрос
    sql = mock_cursor.execute.call_args[0][0]
    assert "INSERT INTO users" in sql
    # Проверяем данные (второй аргумент — кортеж с данными)
    data = mock_cursor.execute.call_args[0][1]
    assert data[0] == "123"      # chat_id
    assert data[1] == "TestUser"  # name
    assert data[2] == "Moscow"    # city
    assert data[3] == "08:00"     # time
    assert data[5] == "ready"     # state
    assert data[6] == 10800       # timezone_offset
    
    # Проверяем, что изменения сохранены
    mock_conn.commit.assert_called_once()


def test_get_user_from_bd_exists(mock_db_connection):
    """
    Проверяем, что get_user_from_bd() возвращает словарь с данными пользователя,
    если пользователь найден.
    """
    mock_conn, mock_cursor = mock_db_connection
    
    # Настраиваем мок: fetchone() возвращает кортеж с данными
    mock_cursor.fetchone.return_value = ("123", "TestUser", "Moscow", "08:00", "2026-08-28", "ready", 10800)
    
    # Вызываем функцию
    result = get_user_from_bd("123")
    
    # Проверяем, что запрос выполнен с правильным chat_id
    mock_cursor.execute.assert_called_once()
    sql = mock_cursor.execute.call_args[0][0]
    assert "SELECT * FROM users" in sql
    data = mock_cursor.execute.call_args[0][1]
    assert data[0] == "123"
    
    # Проверяем, что результат — правильный словарь
    assert result["chat_id"] == "123"
    assert result["name"] == "TestUser"
    assert result["city"] == "Moscow"
    assert result["time"] == "08:00"
    assert result["last_sent"] == "2026-08-28"
    assert result["state"] == "ready"
    assert result["timezone_offset"] == 10800


def test_get_user_from_bd_not_exists(mock_db_connection):
    """
    Проверяем, что если пользователь не найден, возвращается None.
    """
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None  # пользователь не найден
    
    result = get_user_from_bd("999")
    
    assert result is None


def test_get_all_users_from_bd(mock_db_connection):
    """
    Проверяем, что get_all_users_from_bd() возвращает список всех пользователей.
    """
    mock_conn, mock_cursor = mock_db_connection
    
    # Настраиваем мок: fetchall() возвращает список кортежей
    mock_cursor.fetchall.return_value = [
        ("123", "User1", "Moscow", "08:00", "2026-08-28", "ready", 10800),
        ("456", "User2", "London", "09:00", None, "ready", 0)
    ]
    
    # Вызываем функцию
    results = get_all_users_from_bd()
    
    # Проверяем, что запрос был выполнен
    mock_cursor.execute.assert_called_once()
    
    # Проверяем результат
    assert len(results) == 2
    assert results[0]["chat_id"] == "123"
    assert results[0]["name"] == "User1"
    assert results[1]["chat_id"] == "456"
    assert results[1]["city"] == "London"
    assert results[1]["last_sent"] is None  # должно быть None, а не строка


def test_update_last_sent(mock_db_connection):
    """
    Проверяем, что update_last_sent() обновляет поле last_sent.
    """
    mock_conn, mock_cursor = mock_db_connection
    
    # Вызываем функцию
    update_last_sent("123")
    
    # Проверяем, что выполнен UPDATE с правильным chat_id
    mock_cursor.execute.assert_called_once()
    sql = mock_cursor.execute.call_args[0][0]
    assert "UPDATE users SET last_sent = " in sql
    data = mock_cursor.execute.call_args[0][1]
    assert data[1] == "123"  # второй параметр — chat_id
    
    # Проверяем, что изменения сохранены
    mock_conn.commit.assert_called_once()