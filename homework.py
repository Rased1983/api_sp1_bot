import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

import requests
from dotenv import load_dotenv
from telegram import Bot


load_dotenv()

file_for_handler = os.path.dirname(os.path.join(__file__)) + 'log.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(message)s',
    handlers=[
        RotatingFileHandler(
            file_for_handler,
            maxBytes=1000000, backupCount=5,
        ),
        logging.StreamHandler()
    ]
)

try:
    PRAKTIKUM_TOKEN = os.environ['PRAKTIKUM_TOKEN']
    TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
    CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
except KeyError as e:
    logging.error(f'Input data error: {e}')
    sys.exit()

HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
STATUSES = {'reviewing': 'Работа взята на ревью, ожидайте результат',
            'rejected': 'К сожалению, в работе нашлись ошибки.',
            'approved': 'Ревьюеру всё понравилось, работа зачтена!'}

URL = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

bot = Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if homework_name is None:
        message = 'Not homework name.'
        logging.exception(message)
        return message
    if status not in STATUSES:
        message = 'Not homework status.'
        logging.exception(message)
        return message
    verdict = STATUSES[status]
    if status == 'reviewing':
        return verdict
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL, headers=HEADERS, params=payload)
        return homework_statuses.json()
    except requests.exceptions.HTTPError as e:
        logging.exception(f'Request with an error: {e}')
    except ValueError as e:
        logging.exception(f'Request with an error: {e}')
    return {}


def send_message(message):
    bot.send_message(CHAT_ID, message)
    logging.info(f'A message has been sent to telegram: {message}')


def main():
    logging.debug('Бот запущен!')
    current_timestamp = int(time.time())
    while True:
        try:
            homework = get_homeworks(current_timestamp)
            homework_status = homework.get('homeworks')
            if homework_status:
                message = parse_homework_status(homework_status[0])
                send_message(message)
            current_date = homework.get('current_date')
            current_timestamp = current_date or int(time.time())
            time.sleep(10 * 60)  # Опрашивать раз в 10 минут

        except Exception as e:
            message = f'Bot died with an error: {e}'
            logging.error(message)
            send_message(message)
            time.sleep(5 * 60)


if __name__ == '__main__':
    main()
