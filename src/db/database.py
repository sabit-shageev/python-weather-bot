# db/database.py

import sqlite3
from datetime import datetime
from config import DB_NAME


def init_db():
    """
    Создаёт таблицу пользователей, если она ещё не существует.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id TEXT PRIMARY KEY,
            name TEXT,
            city TEXT,
            time TEXT,
            last_sent TEXT,
            state TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_user_to_bd(chat_id, name, city, time_value, state, last_sent=None):
    """
    Сохраняет или обновляет пользователя.
    
    INSERT OR REPLACE:
    - если user есть → обновит
    - если нет → создаст
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO users (chat_id, name, city, time, last_sent, state)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (chat_id, name, city, time_value, last_sent, state))

    conn.commit()
    conn.close()


def get_user_from_bd(chat_id):
    """
    Получает пользователя по chat_id.
    Возвращает словарь или None.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()

    conn.close()

    if row:
        return {
            "chat_id": row[0],
            "name": row[1],
            "city": row[2],
            "time": row[3],
            "last_sent": row[4],
            "state": row[5]
        }

    return None


def get_all_users_from_bd():
    """
    Возвращает список всех пользователей.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    conn.close()

    # Преобразуем список кортежей в список словарей
    return [
        {
            "chat_id": row[0],
            "name": row[1],
            "city": row[2],
            "time": row[3],
            "last_sent": row[4],
            "state": row[5]
        }
        for row in rows
    ]


def update_last_sent(chat_id):
    """
    Обновляет дату последней отправки сообщения.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        UPDATE users SET last_sent = ? WHERE chat_id = ?
    """, (today, chat_id))

    conn.commit()
    conn.close()