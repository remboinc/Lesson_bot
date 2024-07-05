# Телеграм-бот, оповещающий о проверке работ
Этот бот оповещает о проверке работ на сайте dvmn.org.
## Как начать
Для запуска понадобится Python третьей версии.

Скачайте код с GitHub. 

```sh
git clone https://github.com/remboinc/Lesson_bot.git
```
Затем установите зависимости

```sh
pip install -r requirements.txt
```
Создайте файл ```.env```, вставьте в него свой chat_id, dvmn_token и токен телеграм бота.

```sh
TELEGRAM_BOT_TOKEN='21234567:роиоОРПпоро7пгороyDIH8FcoNLGGdF4twQ'
TG_CHAT_ID=123456789
DVMN_TOKEN=r34hf38434h83fjruieiurhf834h74802djidji
```
Запустите скрипт
```sh
python main.py
```
