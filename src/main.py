# =========================
# ИМПОРТЫ
# =========================

# requests — библиотека для HTTP-запросов (мы используем её для обращения к API)
import requests

# time — используется для задержек (sleep), чтобы не нагружать процессор
import time

# datetime — работа с датой и временем (нужно для рассылки по времени)
from datetime import datetime

# re — регулярные выражения (проверка формата времени)
import re

# sqlite3 — встроенная база данных SQLite
import sqlite3


# =========================
# КОНФИГУРАЦИЯ
# =========================

# Токен Telegram-бота (в реальном проекте должен храниться в переменных окружения)
TOKEN = "8611652469:AAH7x1nNV0PZSzFTXh7mSIyAcqnowC3eYIk"

# Базовый URL для Telegram API
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"

# API ключ для сервиса погоды (OpenWeatherMap)
WEATHER_API_KEY = "2f8e69c290879788ede58c0c7e759957"

# Имя файла базы данных SQLite (будет создан автоматически)
DB_NAME = "users.db"


# =========================
# СОСТОЯНИЯ ПОЛЬЗОВАТЕЛЯ
# =========================

# Пользователь только начал диалог и должен ввести данные
STATE_WAITING_INFO = "waiting_for_info"

# Пользователь полностью настроен и готов получать рассылку
STATE_READY = "ready"


# =========================
# РАБОТА С БАЗОЙ ДАННЫХ
# =========================

def init_db():
    """
    Создание таблицы users, если она еще не существует.

    CREATE TABLE IF NOT EXISTS — SQL-команда, которая:
    - создает таблицу, если ее нет
    - ничего не делает, если таблица уже существует

    Поля:
    chat_id   — уникальный идентификатор пользователя в Telegram
    name      — имя пользователя
    city      — город
    time      — время получения рассылки
    last_sent — дата последней отправки (нужно, чтобы не отправлять несколько раз в день)
    state     — текущее состояние пользователя
    """

    conn = sqlite3.connect(DB_NAME)  # подключение к базе (или создание файла)
    cursor = conn.cursor()           # объект для выполнения SQL-запросов

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

    conn.commit()  # применяем изменения
    conn.close()   # закрываем соединение


def save_user(chat_id, name, city, time_value, state, last_sent=None):
    """
    Сохраняет или обновляет пользователя в базе данных.

    INSERT OR REPLACE — важная конструкция:
    - если записи с таким chat_id нет → создаёт новую
    - если есть → полностью заменяет

    ? — это placeholder (плейсхолдер), защита от SQL-инъекций.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO users (chat_id, name, city, time, last_sent, state)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (chat_id, name, city, time_value, last_sent, state))

    conn.commit()
    conn.close()


def get_user(chat_id):
    """
    Получает одного пользователя по chat_id.

    fetchone() возвращает одну строку из результата запроса.
    Если пользователь не найден — вернется None.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()

    conn.close()

    if row:
        # Преобразуем кортеж из БД в словарь для удобства
        return {
            "chat_id": row[0],
            "name": row[1],
            "city": row[2],
            "time": row[3],
            "last_sent": row[4],
            "state": row[5],
        }

    return None


def get_all_users():
    """
    Возвращает список всех пользователей из базы.

    fetchall() возвращает список всех строк результата.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    conn.close()

    users = []
    for row in rows:
        users.append({
            "chat_id": row[0],
            "name": row[1],
            "city": row[2],
            "time": row[3],
            "last_sent": row[4],
            "state": row[5],
        })

    return users


def update_last_sent(chat_id):
    """
    Обновляет дату последней отправки сообщения пользователю.

    Это нужно для того, чтобы:
    - не отправлять сообщение несколько раз в течение одного дня
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        UPDATE users SET last_sent = ? WHERE chat_id = ?
    """, (today, chat_id))

    conn.commit()
    conn.close()


# =========================
# ВАЛИДАЦИЯ ДАННЫХ
# =========================

def is_valid_time(time_str):
    """
    Проверяет, что время введено в формате HH:MM.

    Регулярное выражение ^\d{2}:\d{2}$ означает:
    - ровно 2 цифры
    - двоеточие
    - ровно 2 цифры

    Затем дополнительно проверяем диапазон часов и минут.
    """

    pattern = r"^\d{2}:\d{2}$"

    if not re.match(pattern, time_str):
        return False

    hours, minutes = map(int, time_str.split(":"))

    return 0 <= hours < 24 and 0 <= minutes < 60


def is_valid_city(city):
    """
    Проверяет, существует ли город.

    Для этого делаем запрос к API погоды.
    Если статус ответа 200 — город найден.
    """

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}"
        return requests.get(url, timeout=5).status_code == 200
    except:
        return False


def is_time_to_send(user_time):
    """
    Проверяет, совпадает ли текущее время с временем пользователя.
    """

    return datetime.now().strftime("%H:%M") == user_time


def already_sent_today(user):
    """
    Проверяет, отправляли ли уже сообщение сегодня.
    """

    return user["last_sent"] == datetime.now().strftime("%Y-%m-%d")


# =========================
# TELEGRAM API
# =========================

def get_updates(offset=None):
    """
    Получение новых сообщений от Telegram.

    offset — используется, чтобы не получать старые сообщения повторно.

    timeout=100 — long polling:
    сервер будет держать соединение до 100 секунд, ожидая новые сообщения.
    """

    try:
        url = f"{TELEGRAM_URL}/getUpdates"
        params = {"timeout": 100, "offset": offset}
        return requests.get(url, params=params).json()
    except:
        return {"result": []}


def send_message(chat_id, text):
    """
    Отправка сообщения пользователю через Telegram API.
    """

    url = f"{TELEGRAM_URL}/sendMessage"
    requests.get(url, params={"chat_id": chat_id, "text": text})


# =========================
# ПОЛУЧЕНИЕ ПОГОДЫ
# =========================

def get_weather_emoji(weather_id):
    """
    Возвращает эмодзи в зависимости от погодного кода.
    """

    if 200 <= weather_id < 300:
        return "⛈"
    elif 300 <= weather_id < 400:
        return "🌦"
    elif 500 <= weather_id < 600:
        return "🌧"
    elif 600 <= weather_id < 700:
        return "❄️"
    elif 700 <= weather_id < 800:
        return "🌫"
    elif weather_id == 800:
        return "☀️"
    else:
        return "☁️"


def get_weather(city):
    """
    Получает текущую погоду из API и формирует текст сообщения.
    """

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    data = requests.get(url).json()

    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]
    desc = data["weather"][0]["description"]
    wind_speed = data["wind"]["speed"]
    humidity = data["main"]["humidity"]
    weather_id = data["weather"][0]["id"]

    emoji = get_weather_emoji(weather_id)

    return f"""🌍 Погода в {city}:
        {emoji} {desc.capitalize()}
        🌡 {temp}°C
        🤔 Ощущается как: {feels}°C
        🍃 Скорость ветра: {wind_speed} м/с
        💧 Влажность: {humidity}%"""


# =========================
# ОСНОВНОЙ ЦИКЛ
# =========================

def main():
    print("Бот запущен")
    offset = None

    init_db()

    while True:
        data = get_updates(offset)

        # обработка входящих сообщений
        for update in data["result"]:
            offset = update["update_id"] + 1

            if "message" not in update:
                continue

            message = update["message"]
            chat_id = str(message["chat"]["id"])
            text = message.get("text")

            if not text:
                continue

            user = get_user(chat_id)

            # команда /start
            if text == "/start":
                save_user(chat_id, None, None, None, STATE_WAITING_INFO)

                send_message(chat_id,
                    "Приветствую!\n"
                    "📌 Для дальнейшего взаимодействия, прошу сообщить:\n\n"
                    "1) Как к Вам обращаться?\n" 
                    "2) В каком городе Вы живете\n"
                    "3) Во сколько Вы хотите получать сводку погоды\n\n"
                    "📌 Пример:\n"
                    "Расул Чабдаров, Нальчик, 08:00"
                )
                continue

            # ввод данных
            if user and user["state"] == STATE_WAITING_INFO:
                try:
                    name, city, user_time = [x.strip() for x in text.split(",")]

                    if not is_valid_time(user_time):
                        send_message(chat_id, "Неверный формат времени")
                        continue

                    if not is_valid_city(city):
                        send_message(chat_id, "Город не найден")
                        continue

                    save_user(chat_id, name, city, user_time, STATE_READY)

                    send_message(chat_id, "Данные сохранены")

                except:
                    send_message(chat_id, "Ошибка формата")

        # рассылка
        for user in get_all_users():
            if user["state"] != STATE_READY:
                continue

            if not is_time_to_send(user["time"]):
                continue

            if already_sent_today(user):
                continue

            weather = get_weather(user["city"])

            send_message(user["chat_id"], f"Приветствую, {user['name']}\n\n{weather}")

            update_last_sent(user["chat_id"])

        time.sleep(2)


if __name__ == "__main__":
    main()