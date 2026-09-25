# scheduler/mailing.py

from db.database import get_all_users_from_bd, update_last_sent
from services.validation import already_sent_today
from services.weather import get_weather
from bot.telegram_api import send_message
from config import STATE_READY
from src.logger import setup_logger
from datetime import datetime, timezone, timedelta

logger = setup_logger("mailing")


def process_mailing():
    logger.info("🔄 Проверка рассылки...")
    now_utc = datetime.now(timezone.utc)

    for user in get_all_users_from_bd():
        if user["state"] != STATE_READY:
            continue

        offset_seconds = user.get("timezone_offset", 0)
        local_time = now_utc + timedelta(seconds=offset_seconds)
        local_time_str = local_time.strftime("%H:%M")

        # Прямое сравнение вместо is_time_to_send
        if local_time_str != user["time"]:
            continue

        # Проверка — уже отправляли сегодня?
        if already_sent_today(user):
            continue

        weather = get_weather(user["city"])
        send_message(user["chat_id"], f"Привет, {user['name']}\n\n{weather}")

        # Передаём timezone_offset, чтобы дата записалась по локальному времени
        update_last_sent(user["chat_id"], offset_seconds)

        logger.info(
            f"✅ Отправлено пользователю {user['chat_id']} "
            f"в {local_time_str} (UTC+{offset_seconds // 3600})"
        )