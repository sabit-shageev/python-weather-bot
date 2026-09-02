import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv
from src.logger import setup_logger

logger = setup_logger("database")
load_dotenv()

# Конфигурация подключения к PostgreSQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'weatherbot'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASS', '')
}


def get_connection():
    """Возвращает новое соединение с базой данных."""
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """
    Создаёт таблицу users, если она ещё не существует.
    Добавляет колонку timezone_offset, если её нет.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # 1. Создаём таблицу, если её нет
            cur.execute("""
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
            
            # 2. Проверяем, есть ли колонка timezone_offset
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='timezone_offset'
            """)
            
            if not cur.fetchone():
                # 3. Если колонки нет — добавляем
                cur.execute("""
                    ALTER TABLE users ADD COLUMN timezone_offset INTEGER DEFAULT 0
                """)
                logger.info("✅ Добавлена колонка timezone_offset в таблицу users")
            else:
                logger.info("ℹ️ Колонка timezone_offset уже существует")
            
        conn.commit()


def save_user_to_bd(chat_id, name, city, time_value, state, last_sent=None, timezone_offset=0):
    """
    Сохраняет или обновляет пользователя.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (chat_id, name, city, time, last_sent, state, timezone_offset)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (chat_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    city = EXCLUDED.city,
                    time = EXCLUDED.time,
                    last_sent = EXCLUDED.last_sent,
                    state = EXCLUDED.state,
                    timezone_offset = EXCLUDED.timezone_offset
            """, (chat_id, name, city, time_value, last_sent, state, timezone_offset))
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
                    "state": row[5],
                    "timezone_offset": row[6] if len(row) > 6 else 0  # если колонка есть
                }
            return None


def get_all_users_from_bd():
    """
    Возвращает список всех пользователей.
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
                    "state": row[5],
                    "timezone_offset": row[6] if len(row) > 6 else 0
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