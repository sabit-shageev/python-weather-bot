# scheduler/mailing.py

from db.database import get_all_users_from_bd, update_last_sent
from services.validation import is_time_to_send, already_sent_today
from services.weather import get_weather
from bot.telegram_api import send_message
from config import STATE_READY


def process_mailing():
    """
    Обрабатывает рассылку погоды всем пользователям.
    """

    for user in get_all_users_from_bd():

        # Только активные пользователи
        if user["state"] != STATE_READY:
            continue

        # Проверка времени
        if not is_time_to_send(user["time"]):
            continue

        # Уже отправляли сегодня?
        if already_sent_today(user):
            continue

        # Получаем погоду
        weather = get_weather(user["city"])

        # Отправляем
        send_message(
            user["chat_id"],
            f"Привет, {user['name']}\n\n{weather}"
        )

        # Обновляем дату
        update_last_sent(user["chat_id"])