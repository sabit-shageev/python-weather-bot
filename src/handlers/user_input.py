from db.database import save_user_to_bd
from services.validation import is_valid_time, is_valid_city
from config import STATE_READY
from services.weather import get_weather, get_weather_forecast
from db.database import get_user_from_bd
from bot.telegram_api import send_message, send_keyboard
from handlers.start import handle_start
from src.logger import setup_logger

logger = setup_logger("user_input")

def handle_user_input(chat_id, text):
    """
    Обрабатывает ввод пользователя:
    Имя, Город, Время
    """

    try:

        parts = [x.strip() for x in text.split(",")]

        if len(parts) != 3:
            send_message(chat_id, "Используй формат: Имя, Город, 08:00")
            return

        name, city, user_time = parts       

        # Проверка города
        if not is_valid_city(city):
            send_message(chat_id, "Город не найден\nПопробуйте еще раз\nИспользуй формат: Имя, Город, 08:00")
            return

        # Проверка времени
        if not is_valid_time(user_time):
            send_message(chat_id, "Неверный формат времени")
            return



        # Сохраняем пользователя
        save_user_to_bd(chat_id, name, city, user_time, STATE_READY)

        send_message(
            chat_id,
            f"Готово, {name}. Теперь буду присылать погоду"
        )
        
        send_keyboard(chat_id, "Выберите действие:")

    except Exception as e:
        logger.warning(e)
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
        handle_start(chat_id)
        # send_message(chat_id, "Введи данные заново:\nИмя, Город, Время", remove_keyboard=True)
        