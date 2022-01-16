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
tz = timezone_dict.get(TZ_ENV)
bool = True if HOST != "" and USER != "" and DATABASE != "" and TOKEN != "" and TZ_ENV != "" else False


if __name__ == "__main__":
    if bool:
        print(f"Current TimeZone : {tz}")
        print("Starting Reminder Pengumuman")
        while 1:
            noow = convert_to_utc(datetime.now(timezone(tz)))
            with create_conn() as conn:
                cursor = conn.cursor()
                query = "SELECT jurusan, prodi, tingkat, isi FROM isi_pengumuman WHERE tanggal = %s"
                val = (noow,)
                cursor.execute(query, val)
                result_set = cursor.fetchone()
                if result_set != None:
                    # for i in result_set:
                    get = f"SELECT id_tele FROM siswa WHERE jurusan = {result_set[0]} AND prodi = {result_set[1]} " \
                            f"AND tingkat = {result_set[2]}"
                    cursor.execute(get)
                    data = cursor.fetchall()
                    tele_id = [tele[0] for tele in data]
                    for tele in tele_id:
                        try:
                            bot.send_message(tele, result_set[3])
                            print(f"Sending to {tele}")
                        except:
                            print(f"Failed to send to {tele}")
                    tele_id.clear()
            sleep(60)

    else:
        print("Silahkan isi ENV file")