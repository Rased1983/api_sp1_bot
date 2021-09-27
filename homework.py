from dotenv import load_dotenv
import logging
import os
import requests
import time
from telegram import Bot


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

bot = Bot(token=TELEGRAM_TOKEN)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
    handlers=[
        logging.FileHandler('log.log', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    status = homework['status']
    if status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(URL, headers=headers, params=payload)
    return homework_statuses.json()


def send_message(message):
    logger.info('Сообщение в Телегу отправлено!')
    return bot.send_message(CHAT_ID, message)


def main():
    logger.debug('Бот запущен!')
    current_timestamp = int(time.time())
    while True:
        try:
            homework = get_homeworks(current_timestamp)
            if homework['homeworks']:
                send_message(parse_homework_status(homework['homeworks'][0]))
            current_timestamp = homework['current_date']
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            logger.error(f'Бот упал с ошибкой: {e}')
            send_message(f'Бот упал с ошибкой: {e}')
            time.sleep(5 * 60)


if __name__ == '__main__':
    main()
