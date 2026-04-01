import requests
import json
from config import TELEGRAM_URL


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
        print("get_updates error:", e)
        return {"result": []}


def send_message(chat_id, text):
    """
    Отправляет обычное сообщение пользователю.
    """
    try:
        url = f"{TELEGRAM_URL}/sendMessage"

        requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text
            },
            timeout=5
        )

    except Exception as e:
        print("send_message error:", e)


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