import os

from mysql import connector
from dotenv import load_dotenv
from datetime import datetime
from time import sleep

load_dotenv()
host = os.environ.get("HOST")
user = "root"
password = os.environ.get("PASSWORD")
database = os.environ.get("DATABASE")

def logfunc(type : str, e : Exception):
    type = str(type).upper()
    with open("logbot.txt", "a") as log:
        log.write(f"{type} ERROR : {e}\n" )

def create_conn():
    try:
        db = connector.connect(host=host, user=user, password=password, database=database, autocommit=True)
        return db
    except Exception as e:
        print(e)
        logfunc("DB CONN NOT CREATED", e)


def checkuser(telegramid : int):
    with create_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM user WHERE id_tele ={telegramid}")
        user = cursor.fetchone()
        cursor.close()
        if user[0] != 0:
            return True
        else:
            return False

def converttodate(tanggal:str):
    date_time = datetime.strptime(tanggal,'%d/%m/%Y %H:%M')
    return date_time

def auto_update(bot):
    noow = datetime.now().strftime("%Y-%m-%d %H:%M")
    with create_conn() as conn:
        cursor = conn.cursor()
        query = "SELECT jurusan, prodi, tingkat, isi FROM isi_pengumuman WHERE tanggal = %s "  #
        val = (noow,)
        cursor.execute(query, val)  #
        result_set = cursor.fetchone()
        if result_set != None:
            # for i in result_set:
            get = f"SELECT id_tele FROM siswa WHERE jurusan = {result_set[0]} AND prodi = {result_set[1]} " \
                  f"AND tingkat = {result_set[2]}"
            cursor.execute(get)
            data = cursor.fetchall()
            tele_id = [tele[0] for tele in data]
            print(tele_id)
            while len(tele_id) != 0:
                for teleg in tele_id:
                    print("Message Found.... Sending")
                    bot.send_message(int(teleg), str(result_set[3]))
                    tele_id.remove(teleg)
                    print(tele_id)