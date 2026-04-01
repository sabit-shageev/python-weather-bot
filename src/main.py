import time

from db.database import init_db, get_user_from_bd
from bot.telegram_api import get_updates_from_tg

from handlers.start import handle_start
from handlers.user_input import handle_user_input, handle_user_actions

from scheduler.mailing import process_mailing

from config import STATE_WAITING_INFO, STATE_READY


def main():
    print("🤖 Бот запущен")

    init_db()
    offset = None

    while True:
        try:
            data = get_updates_from_tg(offset)

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                if "message" not in update:
                    continue

                message = update["message"]
                chat_id = str(message["chat"]["id"])
                text = message.get("text")

                if not text:
                    continue

                # 🔍 для дебага (очень полезно)
                print(f"[{chat_id}] -> {text}")

                # ===== ПОЛУЧАЕМ ПОЛЬЗОВАТЕЛЯ =====
                user = get_user_from_bd(chat_id)

                # =================================================
                # 🔥 1. /start ВСЕГДА ПЕРВЫЙ (это КРИТИЧНО)
                # =================================================
                if text == "/start":
                    handle_start(chat_id)
                    continue

                # =================================================
                # 🔥 2. ЕСЛИ ПОЛЬЗОВАТЕЛЯ НЕТ → СОЗДАЁМ
                # =================================================
                if not user:
                    handle_start(chat_id)
                    continue

                state = user.get("state")

                # =================================================
                # 🔥 3. ГОТОВЫЙ ПОЛЬЗОВАТЕЛЬ (КНОПКИ)
                # =================================================
                if state == STATE_READY:
                    handle_user_actions(chat_id, text)
                    continue

                # =================================================
                # 🔥 4. РЕГИСТРАЦИЯ
                # =================================================
                if state == STATE_WAITING_INFO:
                    handle_user_input(chat_id, text)
                    continue

                # =================================================
                # 🔥 5. FALLBACK (если вдруг состояние сломалось)
                # =================================================
                handle_start(chat_id)

            # =====================================================
            # 🔥 РАССЫЛКА
            # =====================================================
            process_mailing()

            time.sleep(2)

        except Exception as e:
            print(f"❌ Ошибка в main loop: {e}")
            time.sleep(2)


if __name__ == "__main__":
    main()