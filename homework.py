import os
import time
import logging
import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    homework_name = homework.get('lesson_name')
    if homework.get('status') == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
        
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    homework_statuses = requests.get(URL, headers=headers, params=params)
    try:
        return homework_statuses.json()
    except requests.exceptions.HTTPError as e:
        logging.error(e, exc_info=True)
    



def send_message(message, bot_client):    
    return bot_client.send_message(CHAT_ID, message)


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    # проинициализировать бота здесь
    current_timestamp = int(time.time()) # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]), bot_client)
                logging.info('Сообщение отправлено')
            current_timestamp = new_homework.get('current_date', current_timestamp)  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
