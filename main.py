import os
import time
import requests
import telegram
import logging
from requests.exceptions import ReadTimeout, ConnectionError
from dotenv import load_dotenv


def main():
    load_dotenv()
    chat_id = os.getenv('TG_CHAT_ID')
    telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    dvmn_api_token = os.getenv('DVMN_TOKEN')

    if not all([chat_id, telegram_bot_token, dvmn_api_token]):
        logging.error("Не удалось загрузить одну или несколько переменных окружения.")
        raise ValueError("Не удалось загрузить одну или несколько переменных окружения.")

    bot = telegram.Bot(token=telegram_bot_token)
    params = {}

    while True:
        headers = {"Authorization": f"Token {dvmn_api_token}"}
        long_polling_url = "https://dvmn.org/api/long_polling/"

        try:
            logging.info("Отправка запроса к API DVMN...")
            response = requests.get(long_polling_url, headers=headers, params=params, timeout=90)
            response.raise_for_status()
            logging.info("Ответ получен от API DVMN.")

            lesson_check_results = response.json()
            new_attempts = lesson_check_results.get('new_attempts')
            logging.info(f"Новые попытки: {new_attempts}")

            if new_attempts and len(new_attempts) > 0:
                first_attempt = new_attempts[0]
                lesson_title = first_attempt.get('lesson_title')
                is_negative = first_attempt.get('is_negative')

                if lesson_title:
                    if is_negative:
                        logging.info(f"Отправка негативного отзыва для {lesson_title}")
                        bot.send_message(
                            chat_id=chat_id,
                            text=f'Преподаватель проверил работу "{lesson_title}"\n\nЕсть над чем поработать'
                        )
                    else:
                        logging.info(f"Отправка положительного отзыва для {lesson_title}")
                        bot.send_message(
                            chat_id=chat_id,
                            text=f'Урок "{lesson_title}" сдан!'
                        )

            if lesson_check_results.get('status') == 'timeout':
                params = {"timestamp": lesson_check_results.get('timestamp_to_request')}
                continue

        except ReadTimeout:
            logging.warning("Превышено время ожидания ответа, повторная попытка...")
            continue
        except ConnectionError:
            logging.warning("Ошибка соединения, повторная попытка...")
            time.sleep(1)
            continue
        except TimeoutError:
            logging.warning("Ошибка таймаута, повторная попытка...")
            time.sleep(1)
            continue
        except Exception as e:
            logging.error(f"Неожиданная ошибка: {e}")
            time.sleep(1)
            continue


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("lesson_bot.log"),
            logging.StreamHandler()
        ]
    )
    main()
