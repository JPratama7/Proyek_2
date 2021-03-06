import os, time

import pytz
from mysql import connector
from dotenv import load_dotenv
from datetime import datetime
from pytz import timezone
import random as rand


load_dotenv()
host = os.environ.get("HOST")
user = "root"
password = os.environ.get("PASSWORD")
database = os.environ.get("DATABASE")
TZ_ENV = os.getenv('TIMEZONE')


# Variables for timezone
timezone_dict = {"WIB": "Asia/Jakarta", "WITA": "Asia/Makassar", "WIT": "Asia/Jayapura"}
format_time = '%d/%m/%Y %H:%M'

date_format = '%d %b %y %H:%M'

if TZ_ENV in timezone_dict:
    os.environ['TZ'] = timezone_dict[TZ_ENV]
    time.tzset()
else:
    raise ValueError('Timezone not found')

def create_random(start: int = 0 , end: int = 9999)-> int:
    rand.seed(rand.randint(0,99999999))
    return rand.randint(start, end)

def logfunc(type : str, e : Exception) -> None:
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


def checkuser(telegramid : int) -> bool:
    with create_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM user WHERE id_tele ={telegramid}")
        user = cursor.fetchone()[0]
        if user == 1:
            return True
        else:
            return False

def checksiswa(telegramid : int) -> bool:
    with create_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM siswa WHERE id_tele ={telegramid}")
        user = cursor.fetchone()[0]
        if user == 1:
            return True
        else:
            return False


# a function convert datetime timezone to UTC
def convert_to_utc(date_time : "Datetime object") -> datetime:
    if not isinstance(date_time, datetime):
        date_time = datetime.strptime(date_time, format_time)

    date_time = date_time.astimezone(pytz.UTC).strftime(format_time)
    date_time = datetime.strptime(date_time, format_time)
    return date_time


# a fucntion convert UTC to timezone
def convert_utc_to_usertz(date_time : "Datetime object", user_timezone : "Destination Timezone"):
    tz_user = timezone(timezone_dict.get(user_timezone))
    if not isinstance(date_time, datetime):
        date_time = datetime.strptime(date_time, format_time)

    date_time = date_time.replace(tzinfo=pytz.UTC)
    date_time = date_time.astimezone(tz_user).strftime(format_time)
    # date_time = date_time.astimezone(timezone(tz_user)).strftime(format_time)
    return date_time

def convert_to_utc_from_user(date_time : "Datetime object") -> datetime:
    date_time = date_time.lower()
    if not isinstance(date_time, datetime):
        date_time = datetime.strptime(date_time, date_format)
    date_time = date_time.astimezone(pytz.UTC).strftime(date_format)
    date_time = datetime.strptime(date_time, date_format)
    return date_time

def reminder_tuition(bot : "Telebot Object") -> None:
    with create_conn() as conn:
        cursor = conn.cursor()
        query = "SELECT id_prodi from prodi"
        cursor.execute(query)
        result = cursor.fetchall()
        for i in result:
            query = f"SELECT s.id_tele, (p.spp-s.paid_tuition) FROM siswa s JOIN prodi p WHERE s.prodi = p.id_prodi " \
                        f"AND s.paid_tuition < (SELECT spp FROM prodi WHERE id_prodi = %s) AND s.prodi = %s;"
            cursor.execute(query, (i[0], i[0]))
            result_set = cursor.fetchall()
            if len(result_set) != 0:
                for data in result_set:
                    try:
                        msg = f"""
Pengingat SPP
ID Tele : {data[0]}
Sisa SPP : {data[1]}
                                    """
                        bot.send_message(data[0], msg)
                        print(f"Sending to {data[0]}")
                    except:
                        print(f"Failed to send to {data[0]}")
