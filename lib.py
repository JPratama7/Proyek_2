import os

from mysql import connector
from dotenv import load_dotenv
from datetime import datetime


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