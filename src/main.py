# For imports:
import requests
import time
import json
import os
from datetime import datetime
import re


   # Стадия 1:
    # TODO: Попробовать через библиотеку requests сходить в АПИ бесплатной погоды и получить JSON словарик ответ данных для Санкт Петербурга, 
        # посмотреть на него, порадоваться и скинуть скрин в беседу в ТГ.
        # TODO: Из той инфы, которую выдаст погода, забрать температуру градусов цельсия, пройдясь по python словарику, 
        # и сохранить ее в переменную пока.
"""     
if __name__=="__main__":
 

    API_KEY = "2f8e69c290879788ede58c0c7e759957"
    city = "Saint Petersburg"

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(url)

    data = response.json()

    temperature = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    description = data["weather"][0]["description"]



    print(data)    

    temperature = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    description = data["weather"][0]["description"]
    wind_speed = data["wind"]["speed"]
    humidity = data["main"]["humidity"]

    print(f"Температура: {temperature}°C")
    print(f"Ощущается как: {feels_like}°C")
    print(f"Общая ситуация: {description}")
    print(f"Скорость ветра: {wind_speed}")
    print(f"Влажность: {humidity}")
"""   
    # TODO: Со своего ТГ аккаунту начать чат с созданным ботом.
    # TODO: Выяснить свой chat_id в телеге доступными сейчас современными способами, погуглив их 
        # (вроде был бот, которому ты пишешь, а он тебе в ответ айдишник)
        # либо ты после того как начинаешь чат с ботом, ищещь апи ендпоинт, по которому можно обновления бота посмотреть, 
        # там в урле будет слово "updates" и смотришь, собираешь урл со своим токеном, смотришь в бразуере с компа, че там нового буедт на страничке, 
        # в JSONке на траническ увидешь первое сообщение от своего тг акка боту и там же chat_id
    # TODO: Возможно поиск новых айди можно автоматизировать, велкам!
    # TODO: Написать с бота человеку с погодой!
# Стадия 2:
    # TODO: Нужен while True цикл, в котором ты проверяешь, что сейчас 8 утра.
    # TODO: Собиарешь погоду по Питеру.
    # TODO: Шлешь тем людям, кто ботом начал пользоваться.

    # Стадия 3:
    # TODO: Узнать как правильно ботом реагировать на новые сообщения от пользователей.
    # TODO: Хранить больше инфы об типах (как к нему обращаться вежливо, какой город, в какое время, какое часовой пояс, может даже он несколько локаций)
    # TODO: Tiny DB, можно постоянно читать и писать в JSON файлик (попробовать сделать настоящую реаляционную SQL бд с табличками, в идеале докер файл и мочь коннектиться к БД внутри контейнера)

TOKEN = "8611652469:AAH7x1nNV0PZSzFTXh7mSIyAcqnowC3eYIk"
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"
WEATHER_API_KEY = "2f8e69c290879788ede58c0c7e759957"

USERS_FILE = "users.json"

STATE_WAITING_INFO = "waiting_for_info"
STATE_READY = "ready"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def is_valid_time(time_str):
    pattern = r"^\d{2}:\d{2}$"

    if not re.match(pattern, time_str):
        return False

    hours, minutes = map(int, time_str.split(":"))

    return 0 <= hours < 24 and 0 <= minutes < 60

def is_valid_city(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def get_updates(offset=None):
    url = f"{TELEGRAM_URL}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    response = requests.get(url, params=params)
    return response.json()

def send_message(chat_id, text):
    url = f"{TELEGRAM_URL}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    requests.get(url, params=params)

def get_weather_emoji(weather_id):
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
    elif 801 <= weather_id <= 804:
        return "☁️"
    else:
        return "🌍"
    
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)

    if response.status_code != 200:
        return "Не удалось получить погоду 😢"

    data = response.json()

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

def is_time_to_send(user_time):
    current_time = datetime.now().strftime("%H:%M")
    return current_time == user_time

def main():
    print("Бот запущен...")
    offset = None
    users = load_users()



    while True:
        data = get_updates(offset)

        for update in data["result"]:
            offset = update["update_id"] + 1

            if "message" not in update:
                continue

            message = update["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text")

            if not text:
                continue

            print(f"Сообщение от {chat_id}: {text}")
            
            if text == "/start":
                users[chat_id] = {
                    "state": STATE_WAITING_INFO,
                    "name": None,
                    "city": None,
                    "time": None
                }

                save_users(users)

                send_message(
                    chat_id,
                    "Ва-алейкум ас-салям ва-рахматуллахи ва-баракатух!\n\n"
                    "Я буду присылать Вам погоду каждый день.\n\n"
                    "📌 Для дальнейшего взаимодействия, прошу сообщить:\n\n"
                    "1) Как к Вам обращаться?\n" 
                    "2) В каком городе Вы живете\n"
                    "3) Во сколько Вы хотите получать сводку погоды\n\n"
                    "📌 Пример:\n"
                    "Расул Чабдаров, Нальчик, 08:00"
                )
                continue

            # =========================
            # ПОЛУЧЕНИЕ ДАННЫХ ОТ ПОЛЬЗОВАТЕЛЯ
            # =========================
            if users.get(chat_id, {}).get("state") == STATE_WAITING_INFO:
                try:
                    name, city, user_time = [x.strip() for x in text.split(",")]

                    if not is_valid_time(user_time):
                        send_message(
                            chat_id,
                            "❌ Неверный формат времени.\n\nИспользуй HH:MM\nПример: 08:00"
                        )
                        continue

                    # ✅ проверка города
                    if not is_valid_city(city):
                        send_message(
                            chat_id,
                            "❌ Город не найден.\n\nПопробуй написать еще раз, например: Нальчик"
                        )
                        continue




                    users[chat_id] = {
                        "state": STATE_READY,
                        "name": name,
                        "city": city,
                        "time": user_time
                    }

                    save_users(users)

                    send_message(
                        chat_id,
                        f"✅ Отлично, {name}!\n"
                        f"📍 Город: {city}\n"
                        f"⏰ Время: {user_time}\n\n"
                        "Теперь я буду присылать тебе погоду автоматически! 🚀"
                    )

                except:
                    send_message(
                        chat_id,
                        "❗ Ошибка формата.\n\n"
                        "Используй формат:\n"
                        "Имя, Город, Время\n\n"
                        "Пример:\n"
                        "Расул Чабдаров, Нальчик, 08:00"
                    )

                continue

        # =========================
        # ⏰ РАССЫЛКА ПО ВРЕМЕНИ
        # =========================
        for chat_id, user in users.items():
            if user["state"] != STATE_READY:
                continue

            if is_time_to_send(user["time"]):
                weather = get_weather(user["city"])

                message = f"Ва-алейкум ас-салям ва-рахматуллахи ва-баракатух, {user['name']}!\n\n{weather}"

                send_message(chat_id, message)

                # ❗ чтобы не отправлять много раз за одну минуту
                time.sleep(60)

        # Пауза между циклами
        time.sleep(1)



if __name__ == "__main__":
    main()


  





    

