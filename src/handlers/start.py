from db.database import save_user_to_bd
from bot.telegram_api import send_keyboard
from config import STATE_WAITING_INFO


def handle_start(chat_id):
    """
    Обрабатывает команду /start
    """

    # Сохраняем пользователя в состоянии ожидания данных
    save_user_to_bd(chat_id, None, None, None, STATE_WAITING_INFO)

    send_keyboard(
        chat_id,
        """
Приветствую!
📌 Для дальнейшего взаимодействия, прошу сообщить:

1) Как к Вам обращаться?
2) В каком городе Вы живете
3) Во сколько Вы хотите получать сводку погоды

📌 Пример:
Расул Чабдаров, Нальчик, 08:00
        """
    )