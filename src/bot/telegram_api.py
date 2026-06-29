import requests
import json
from config import TELEGRAM_URL
from src.logger import setup_logger

logger = setup_logger("telegram_api")


def get_updates_from_tg(offset=None):
    """
    Получает новые сообщения от Telegram.
    offset — чтобы не получать старые сообщения повторно.
    """
    try:
        url = f"{TELEGRAM_URL}/getUpdates"
        params = {
            "timeout": 100,
            "offset": offset
        }

        response = requests.get(url, params=params, timeout=110)
        return response.json()

    except Exception as e:
        logger.error(f"get_updates error: {e}", exc_info=True)
        return {"result": []}


def send_message(chat_id, text, remove_keyboard=False):
    url = f"{TELEGRAM_URL}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if remove_keyboard:
        payload["reply_markup"] = {
            "remove_keyboard": True
        }

    requests.post(url, json=payload)

def send_keyboard(chat_id, text):
    url = f"{TELEGRAM_URL}/sendMessage"

    keyboard = {
        "keyboard": [
            [{"text": "🌤 Текущая погода"}],
            [{"text": "📊 Прогноз на сутки"}],
            [{"text": "⚙️ Настройки"}]
        ],
        "resize_keyboard": True
    }

    requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text,
            "reply_markup": keyboard
        },
        timeout=5
    )