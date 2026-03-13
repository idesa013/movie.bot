import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TMBD_API_KEY = os.getenv("TMBD_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
ADMIN_ID = int(os.getenv("ADMIN_ID"))

DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("registration", "Зарегистрироваться"),
)

DATE_FORMAT = "%d.%m.%Y %H:%M"
