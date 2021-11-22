import os

from mysql import connector
from dotenv import load_dotenv, find_dotenv
from os.path import join, dirname


load_dotenv()

def logfunc(type, e):
    type = str(type).upper()
    with open("logbot.txt", "a") as log:
        log.write(f"{type} ERROR : {e}\n" )

def create_conn():
    host = os.environ.get("HOST")
    user = "root"
    password = os.environ.get("PASSWORD")
    database = os.environ.get("DATABASE")
    try:
        db = connector.connect(host=host, user=user, password=password, database=database, autocommit=True)
        return db
    except Exception as e:
        print(e)
        logfunc("DB CONN NOT CREATED", e)


def checkuser(telegramid):
    with create_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM user WHERE id_tele ={telegramid}")
        user = cursor.fetchone()
        cursor.close()
        if user[0] != 0:
            return True
        else:
            return False