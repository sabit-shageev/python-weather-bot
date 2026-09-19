import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv
from config import DB_CONFIG

load_dotenv()


def get_connection():
    """Возвращает новое соединение с базой данных."""
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """
    Создаёт таблицу users, если она ещё не существует.
    Полный аналог старой SQLite-версии.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
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

def save_user_to_bd(chat_id, name, city, time_value, state, last_sent=None):
    """
    Сохраняет или обновляет пользователя.
    В PostgreSQL используем INSERT ... ON CONFLICT (chat_id) DO UPDATE.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (chat_id, name, city, time, last_sent, state)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (chat_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    city = EXCLUDED.city,
                    time = EXCLUDED.time,
                    last_sent = EXCLUDED.last_sent,
                    state = EXCLUDED.state
            """, (chat_id, name, city, time_value, last_sent, state))
        conn.commit()

def get_user_from_bd(chat_id):
    """
    Получает пользователя по chat_id.
    Возвращает словарь или None.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id,))
            row = cur.fetchone()
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
    Возвращает список всех пользователей в виде списка словарей.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users")
            rows = cur.fetchall()
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
    today = datetime.now().strftime("%Y-%m-%d")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users SET last_sent = %s WHERE chat_id = %s
            """, (today, chat_id))
        conn.commit()