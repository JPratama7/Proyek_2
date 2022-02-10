import os

from dotenv import load_dotenv
from datetime import datetime
from lib import create_conn, timezone_dict, convert_to_utc
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
tz = timezone_dict.get(TZ_ENV) if TZ_ENV in timezone_dict else ""
bool = True if HOST != "" and USER != "" and DATABASE != "" and TOKEN != "" and tz != "" else False


if __name__ == "__main__":
    if bool:
        print(f"Current TimeZone : {tz}")
        print("Starting Reminder User")
        while 1:
            noow = convert_to_utc(datetime.now(timezone(tz)))
            with create_conn() as conn:
                cursor = conn.cursor()
                query = "SELECT id_telegram, isi_reminder FROM reminder_user WHERE waktu = %s"
                cursor.execute(query, (noow,))
                result_set = cursor.fetchall()
                if len(result_set) != 0:
                    for data in result_set:
                        try:
                            bot.send_message(data[0], data[1])
                            print(f"Sending to {data[0]}")
                        except:
                            print(f"Failed to send to {data[0]}")

            sleep(60)

    else:
        print("Silahkan isi ENV file")