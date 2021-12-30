import os

import pytz
from mysql import connector
from dotenv import load_dotenv
from datetime import datetime
from pytz import timezone


load_dotenv()
host = os.environ.get("HOST")
user = "root"
password = os.environ.get("PASSWORD")
database = os.environ.get("DATABASE")
TZ_ENV = os.getenv('TIMEZONE')


# Variables for timezone
timezone_dict = {"WIB": "Asia/Jakarta", "WITA": "Asia/Makassar", "WIT": "Asia/Jayapura"}
format_time = '%d/%m/%Y %H:%M'


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
        user = cursor.fetchone()[0]
        if user == 1:
            return True
        else:
            return False

def checksiswa(telegramid : int):
    with create_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM siswa WHERE id_tele ={telegramid}")
        user = cursor.fetchone()[0]
        if user == 1:
            return True
        else:
            return False


# a function convert datetime timezone to UTC
def convert_to_utc(date_time : "Datetime object"):
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