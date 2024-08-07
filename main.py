import os
import time
import requests
import telegram
import logging
from logging import Handler, LogRecord
from systemd.journal import JournalHandler
from requests.exceptions import ReadTimeout, ConnectionError
from dotenv import load_dotenv


logger = logging.getLogger(__name__)


class TelegramHandler(Handler):
    def __init__(self, token, chat_id):
        super().__init__()
        self.bot = telegram.Bot(token=token)
        self.chat_id = chat_id

    def emit(self, record: LogRecord):
        log_entry = self.format(record)
        try:
            self.bot.send_message(chat_id=self.chat_id, text=log_entry)
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения в Telegram: {e}")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(funcName)s %(lineno)d %(levelname)s %(message)s'
    )
    logger.addHandler(JournalHandler())

    load_dotenv()
    chat_id = os.getenv('TG_CHAT_ID')
    telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    dvmn_api_token = os.getenv('DVMN_TOKEN')

    if not all([chat_id, telegram_bot_token, dvmn_api_token]):
        raise ValueError("Не удалось загрузить одну или несколько переменных окружения.")

    try:
        bot = telegram.Bot(token=telegram_bot_token)
        bot.send_message(
            chat_id=chat_id,
            text="Тестовое сообщение для проверки работоспособности бота"
        )
        logging.info("Тестовое сообщение успешно отправлено в Telegram")
    except Exception as e:
        logging.exception("Ошибка при отправке тестового сообщения в Telegram")
        bot.send_message(chat_id=chat_id, text=f"Ошибка при отправке тестового сообщения:\n{e}")

    params = {}

    while True:
        headers = {"Authorization": f"Token {dvmn_api_token}"}
        long_polling_url = "https://dvmn.org/api/long_polling/"

        try:
            logger.info("Отправка запроса к DVMN API...")
            response = requests.get(long_polling_url, headers=headers, params=params, timeout=90)
            response.raise_for_status()
            logger.info("Ответ от DVMN API получен.")

            lesson_check_results = response.json()
            new_attempts = lesson_check_results.get('new_attempts')
            logger.info(f"Новые попытки: {new_attempts}")

            if new_attempts and len(new_attempts) > 0:
                first_attempt = new_attempts[0]
                lesson_title = first_attempt.get('lesson_title')
                is_negative = first_attempt.get('is_negative')

                if lesson_title:
                    if is_negative:
                        logger.info(f"Отправка отрицательного отзыва за {lesson_title}")
                        bot.send_message(
                            chat_id=chat_id,
                            text=f'Преподаватель проверил работу "{lesson_title}"\n\nЕсть над чем поработать'
                        )
                    else:
                        logger.info(f"Отправка положительного отзыва за {lesson_title}")
                        bot.send_message(
                            chat_id=chat_id,
                            text=f'Урок "{lesson_title}" сдан!'
                        )

            if lesson_check_results.get('status') == 'found':
                params = {"timestamp": lesson_check_results.get('timestamp_to_request')}
            else:
                logger.info("Новых попыток нет или запрос не дошел до сервера DVMN, ожидание...")
                time.sleep(10)

        except ReadTimeout:
            logger.error("Произошла ошибка ReadTimeout, повтор запроса...")
            continue
        except ConnectionError:
            logger.error("Произошла ошибка ConnectionError, повтор запроса...")
            time.sleep(1)
            continue
        except TimeoutError:
            logger.error("Произошла ошибка TimeoutError, повтор запроса...")
            time.sleep(1)
            continue
        except Exception as e:
            logger.exception("Неожиданная ошибка")
            bot.send_message(chat_id=chat_id, text=f"Неожиданная ошибка:\n{e}")
            time.sleep(1)
            continue


if __name__ == '__main__':
    main()
