from db.database import save_user_to_bd
from services.validation import is_valid_time, is_valid_city
from bot.telegram_api import send_message
from config import STATE_READY
from services.weather import get_weather, get_weather_forecast
from db.database import get_user_from_bd
from bot.telegram_api import send_message

def handle_user_input(chat_id, text):
    """
    Обрабатывает ввод пользователя:
    Имя, Город, Время
    """

    try:
        name, city, user_time = [x.strip() for x in text.split(",")]

        # Проверка времени
        if not is_valid_time(user_time):
            send_message(chat_id, "Неверный формат времени")
            return

        # Проверка города
        if not is_valid_city(city):
            send_message(chat_id, "Город не найден")
            return

        # Сохраняем пользователя
        save_user_to_bd(chat_id, name, city, user_time, STATE_READY)

        send_message(chat_id, "Данные сохранены")

    except Exception as e:
        print(e)
        send_message(chat_id, "Ошибка формата")

def handle_user_actions(chat_id, text):
    """
    Обрабатывает нажатия кнопок
    """

    user = get_user_from_bd(chat_id)

    if not user or not user["city"]:
        send_message(chat_id, "Сначала настрой бота через /start")
        return

    # Текущая погода
    if text == "🌤 Текущая погода":
        weather = get_weather(user["city"])
        send_message(chat_id, weather)

    # Прогноз
    elif text == "📊 Прогноз на сутки":
        forecast = get_weather_forecast(user["city"])
        send_message(chat_id, forecast)

    # Настройки
    elif text == "⚙️ Настройки":
        send_message(chat_id, "Введи данные заново:\nИмя, Город, Время")