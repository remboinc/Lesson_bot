import os
import time
import requests
import telegram
from requests import ReadTimeout, ConnectionError
from dotenv import load_dotenv


def main():
    load_dotenv()
    chat_id = os.getenv('TG_CHAT_ID')
    telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    dvmn_api_token = os.getenv('DVMN_TOKEN')
    bot = telegram.Bot(token=telegram_bot_token)

    while True:
        headers = {"Authorization": dvmn_api_token}
        long_polling_url = "https://dvmn.org/api/long_polling/"

        try:
            response = requests.get(long_polling_url, headers=headers, params=params)
            response.raise_for_status()
            lesson_check_results = response.json()
            lesson_title = lesson_check_results.get('new_attempts')[0].get('lesson_title')
            if lesson_check_results.get('new_attempts')[0].get('is_negative'):
                bot.send_message(text=f'Преподаватель проверил работу "{lesson_title}"\n\nЕсть над чем поработать',
                                 chat_id=chat_id)
            elif not lesson_check_results.get('new_attempts')[0].get('is_negative'):
                bot.send_message(text=f'Урок /"{lesson_title}/" сдан!',
                                 chat_id=chat_id)
            elif lesson_check_results.get('status') == 'timeout':
                params = {"timestamp": lesson_check_results.get('timestamp_to_request')}
                continue
        except ReadTimeout:
            continue
        except ConnectionError:
            time.sleep(1)
            print('ConnectionError, reload...')
            continue
        except TimeoutError:
            time.sleep(1)
            print('TimeoutError, reload...')
            continue


if __name__ == '__main__':
    main()
