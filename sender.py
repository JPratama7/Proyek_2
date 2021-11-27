import os

from mysql import connector
from dotenv import load_dotenv
from datetime import datetime
from telebot import TeleBot

from lib import create_conn

load_dotenv()

HOST = os.getenv("HOST")
USER = "root"
PASS = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
TOKEN = os.getenv('API')

bool = True if HOST != "" and USER != "" and DATABASE != "" and TOKEN != "" else False

if __name__ == "__main__":
    if bool:
        print(f"Current TimeZone : {datetime.utcnow().astimezone().tzinfo}")
        bot = TeleBot(TOKEN)
        while 1:
            noow = datetime.now().strftime("%Y-%m-%d %H:%M")
            with create_conn() as conn:
                cursor = conn.cursor()
                query = "SELECT jurusan, prodi, tingkat, isi FROM isi_pengumuman WHERE tanggal = %s"
                val = (noow,)
                cursor.execute(query, val)
                result_set = cursor.fetchall()
                if len(result_set) != 1:
                    for i in result_set:
                        get = f"SELECT id_tele FROM siswa WHERE jurusan = {i[0]} AND prodi = {i[1]} " \
                              f"AND tingkat = {i[2]}"
                        cursor.execute(get)
                        data = cursor.fetchall()
                        for teleg in data:
                            bot.send_message(int(teleg[0]), str(i[3]))
    else:
        print("Silahkan isi ENV file")