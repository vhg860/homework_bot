import http
import logging
import os
import sys
import time
from logging import FileHandler, Formatter, StreamHandler

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(stream=sys.stdout)
handler_file = FileHandler(filename='main.log')
handler_file.setLevel(logging.DEBUG)
logger.addHandler(handler)
formatter = Formatter(
    '%(asctime)s, %(levelname)s, %(message)s, %(funcName)s, %(lineno)s'
)
handler.setFormatter(formatter)


def check_tokens():
    """Проверяем доступность переменных окружения."""
    if not all([TELEGRAM_TOKEN, PRACTICUM_TOKEN, TELEGRAM_CHAT_ID]):
        logging.critical('Отсутсвие переменных окружения')
        sys.exit('Отсутсвие переменных окружения')


def send_message(bot, message):
    """Отправляет сообщения в чат."""
    try:
        logger.debug('Начало отправки сообщения')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telegram.TelegramError:
        logger.error('Ошибка отправки сообщения')
    else:
        logger.debug('Сообщение отправлено')


def get_api_answer(timestamp):
    """Запрос к эндпоинту Яндекса."""
    params_request = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp},
    }
    logging.debug(f'Отправка запроса к API-сервису {params_request}.')
    try:
        response = requests.get(**params_request)
        if response.status_code != http.HTTPStatus.OK:
            raise exceptions.InvalidRequest(
                f'Ошибка в получении запроса {response.status_code}'
            )
        return response.json()
    except requests.RequestException:
        raise exceptions.ConnectApiError('Ошибка ответа')


def check_response(response):
    """Проверяем ответ API."""
    logging.debug('Начало проверки ответа сервера.')
    if not isinstance(response, dict):
        raise TypeError(f'Запрос к API вернул не словарь {response}')
    if 'homeworks' not in response:
        raise exceptions.EmptyResponseAPI('Нет ключа homeworks')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('Значение ключа homeworks не list')
    logging.info('Запрос API прошел проверку')
    return homeworks


def parse_status(homework):
    """Получаем статус последней домашней работы."""
    if 'homework_name' not in homework:
        raise exceptions.UnknownStatus('Нет homework_name в homework.')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        massage_error = 'Неизвестный статус работы.'
        raise KeyError(massage_error)
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = 0
    send_message(bot, 'Старт')
    current_report = {'name': '', 'output': ''}
    prev_report = current_report.copy()
    while True:
        try:
            response = get_api_answer(timestamp)
            new_homeworks = check_response(response)

            if new_homeworks:
                current_report['output'] = parse_status(new_homeworks[0])
                current_report['name'] = new_homeworks[0]['homework_name']
            else:
                current_report['output'] = ('Новых работ нет')

            if current_report != prev_report:
                send_message(bot, current_report)
                prev_report = current_report.copy()
            else:
                logging.debug('Статус не изменился.')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            current_report['output'] = message
            logging.error(message)
            if current_report != prev_report:
                send_message(bot, current_report)
                prev_report = current_report.copy()
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
