# scheduler/mailing.py

from db.database import get_all_users_from_bd, update_last_sent
from services.validation import is_time_to_send, already_sent_today
from services.weather import get_weather
from bot.telegram_api import send_message
from config import STATE_READY
from src.logger import setup_logger
from datetime import datetime, timezone, timedelta

logger = setup_logger("mailing")


def process_mailing():
    """
    Обрабатывает рассылку погоды всем пользователям.
    Учитывает часовой пояс каждого пользователя.
    """
    logger.info("🔄 Проверка рассылки...")
    # Текущее время в UTC
    now_utc = datetime.now(timezone.utc)

    for user in get_all_users_from_bd():

        # Только активные пользователи
        if user["state"] != STATE_READY:
            continue

        # Получаем смещение пользователя (в секундах), если нет — 0 (UTC)
        offset_seconds = user.get('timezone_offset', 0)
        
        # Вычисляем локальное время пользователя
        local_time = now_utc + timedelta(seconds=offset_seconds)
        local_time_str = local_time.strftime("%H:%M")

        # Проверка времени (с учётом локального времени пользователя)
        if not is_time_to_send(local_time_str, user['time']):
            continue

        # Проверка, отправляли ли уже сегодня (ЗАКОММЕНТИРОВАНО ДЛЯ ТЕСТА)
        # if already_sent_today(user):
        #     continue

        # Получаем погоду
        weather = get_weather(user["city"])

        # Отправляем
        send_message(
            user["chat_id"],
            f"Привет, {user['name']}\n\n{weather}"
        )

        # Обновляем дату (ЗАКОММЕНТИРОВАНО ДЛЯ ТЕСТА)
        # update_last_sent(user["chat_id"])

        # Логируем отправку
        logger.info(f"✅ Отправлена рассылка пользователю {user['chat_id']} в {local_time_str} (UTC+{offset_seconds//3600})")