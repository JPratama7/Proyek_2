import os

from dotenv import load_dotenv
from datetime import datetime
from lib import create_conn, timezone_dict, convert_to_utc, reminder_tuition
from time import sleep
from telebot import TeleBot
from pytz import timezone

load_dotenv()

HOST = os.getenv("HOST")
USER = "root"
PASS = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
TOKEN = os.getenv('API')
TZ_ENV = os.getenv('TIMEZONE')


bot = TeleBot(TOKEN)
tz = timezone_dict.get(TZ_ENV)
bool = True if HOST != "" and USER != "" and DATABASE != "" and TOKEN != "" and TZ_ENV != "" else False


if __name__ == "__main__":
    if bool:
        print(f"Current TimeZone : {tz}")
        print("Starting Pengingat SPP")
        while 1:
            reminder_tuition(bot)
            sleep(60)

    else:
        print("Silahkan isi ENV file")