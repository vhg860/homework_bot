import logging
import os
import time
import http
from logging.handlers import RotatingFileHandler

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
handler = RotatingFileHandler(
    "main.log",
    maxBytes=50000000,
    backupCount=5,
)
logger.addHandler(handler)
formatter = logging.Formatter(
    "%(asctime)s, %(levelname)s, %(message)s, %(funcName)s, %(lineno)s"
)
handler.setFormatter(formatter)


def check_tokens():
    """Проверяем доступность переменных окружения."""
    env_constans = all([TELEGRAM_TOKEN, PRACTICUM_TOKEN, TELEGRAM_CHAT_ID])
    if not env_constans:
        logging.critical('Отсутсвие переменных окружения')
        exit('Отсутсвие переменных окружения')


def send_message(bot, message):
    """Отправляет сообщения в чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telegram.TelegramError:
        logger.error('Ошибка отправки сообщения')
    else:
        logger.debug('Сообщение отправлено')


def get_api_answer(timestamp):
    """Запрос к эндпоинту Яндекса."""
    logging.debug('Отправка запроса к API-сервиса.')
    try:
        params = {'from_date': timestamp}
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != http.HTTPStatus.OK:
            logging.error('Эндпоинт недоступен')
            raise exceptions.InvalidRequest('Ошибка в получении запроса')
        return response.json()
    except requests.RequestException:
        logging.error('Ошибка ответа')
        raise exceptions.ConnectApiError('Ошибка ответа')


def check_response(response):
    """Проверяем ответ API."""
    try:
        if not isinstance(response, dict):
            logger.error('Запрос к API вернул не словарь')
            raise TypeError('Запрос к API вернул не словарь')
        if 'homeworks' not in response:
            logger.error('Нет ключа homeworks')
            raise KeyError('Нет ключа homeworks')
        if not isinstance(response['homeworks'], list):
            logger.error('Значение ключа homeworks не list')
            raise TypeError('Значение ключа homeworks не list')
        if not response['homeworks']:
            logger.error('Список пуст')
            raise TypeError('Список пуст')
        return response['homeworks']
    except Exception as error:
        logger.error(error)
        raise TypeError(error)


def parse_status(homework):
    """Получаем статус последней домашней работы."""
    if 'homework_name' not in homework:
        logging.error('Нет homework_name в homework.')
        raise exceptions.UnknownStatus('Нет homework_name в homework.')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        massage_error = 'Неизвестный статус работы.'
        logging.error(massage_error)
        raise KeyError(massage_error)
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    send_message(bot, 'Старт')
    start_answer = ''
    while True:
        try:
            new_request = get_api_answer(timestamp)
            check_response(new_request)
            logging.info('Запрос API прошел проверку')
            homeworks = new_request['homeworks']
            if not homeworks:
                logging.info('Нет активной работы')
                continue
            homework = parse_status(homeworks[0])
            if homework != start_answer:
                send_message(bot, homework)
                logging.info(f'Новый статус {homework}')
                start_answer = new_request
                timestamp = new_request.get('current_date')
            else:
                logging.info('Статус не изменился')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
