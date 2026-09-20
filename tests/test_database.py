import pytest
from unittest.mock import MagicMock, patch
from src.db.database import init_db, save_user_to_bd, get_user_from_bd, get_all_users_from_bd, update_last_sent


def test_init_db(mock_db_connection):
    """Тест: создание таблицы"""
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None  # колонки нет
    
    init_db()
    
    # Проверяем, что CREATE TABLE был выполнен
    mock_cursor.execute.assert_any_call("""
                CREATE TABLE IF NOT EXISTS users (
                    chat_id TEXT PRIMARY KEY,
                    name TEXT,
                    city TEXT,
                    time TEXT,
                    last_sent TEXT,
                    state TEXT,
                    timezone_offset INTEGER DEFAULT 0
                )
            """)
    
    # Проверяем, что ALTER TABLE был вызван
    mock_cursor.execute.assert_any_call("""
                    ALTER TABLE users ADD COLUMN timezone_offset INTEGER DEFAULT 0
                """)
    
    mock_conn.commit.assert_called()


def test_init_db_column_exists(mock_db_connection):
    """Тест: создание таблицы, колонка уже существует"""
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = ("timezone_offset",)  # колонка есть
    
    init_db()
    
    # Проверяем, что ALTER TABLE НЕ вызывался
    # Находим все вызовы execute
    calls = [call[0][0] for call in mock_cursor.execute.call_args_list if 'ALTER TABLE' in call[0][0]]
    assert len(calls) == 0


def test_save_user_to_bd(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    
    save_user_to_bd("123", "TestUser", "Moscow", "08:00", "ready", timezone_offset=10800)
    
    mock_cursor.execute.assert_called_once()
    sql = mock_cursor.execute.call_args[0][0]
    assert "INSERT INTO users" in sql
    
    data = mock_cursor.execute.call_args[0][1]
    assert data[0] == "123"
    assert data[1] == "TestUser"
    assert data[2] == "Moscow"
    assert data[3] == "08:00"
    assert data[5] == "ready"
    assert data[6] == 10800
    
    mock_conn.commit.assert_called_once()


def test_get_user_from_bd_exists(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = ("123", "TestUser", "Moscow", "08:00", "2026-09-02", "ready", 10800)
    
    result = get_user_from_bd("123")
    
    assert result["chat_id"] == "123"
    assert result["name"] == "TestUser"
    assert result["city"] == "Moscow"
    assert result["time"] == "08:00"
    assert result["last_sent"] == "2026-09-02"
    assert result["state"] == "ready"
    assert result["timezone_offset"] == 10800


def test_get_user_from_bd_not_exists(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None
    
    result = get_user_from_bd("999")
    assert result is None


def test_get_all_users_from_bd(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        ("123", "User1", "Moscow", "08:00", "2026-09-02", "ready", 10800),
        ("456", "User2", "London", "09:00", None, "ready", 0)
    ]
    
    results = get_all_users_from_bd()
    
    assert len(results) == 2
    assert results[0]["chat_id"] == "123"
    assert results[0]["name"] == "User1"
    assert results[1]["chat_id"] == "456"
    assert results[1]["city"] == "London"


def test_update_last_sent(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    
    update_last_sent("123")
    
    mock_cursor.execute.assert_called_once()
    sql = mock_cursor.execute.call_args[0][0]
    assert "UPDATE users SET last_sent = " in sql
    data = mock_cursor.execute.call_args[0][1]
    assert data[1] == "123"  # chat_id
    mock_conn.commit.assert_called_once()