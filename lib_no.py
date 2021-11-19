import os

from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = str(os.getenv('URL'))
key = str(os.getenv('KEY'))


def logfunc(type, e):
    type = str(type).upper()
    with open("logbot.txt", "a") as log:
        log.write(f"{type} ERROR : {e}\n")


def insert_table(table, data: dict):
    try:
        supabase: Client = create_client(url, key)
        query = supabase.table(f"{table}").insert(data).execute()
    except Exception as e:
        logfunc("DATABASE", e)

def select_table(table: str):
    supabase: Client = create_client(url, key)
    data = supabase.table("user").    data = supabase.table(f"{table}").select("*").execute()
    return data

# insert_table("user", {"id_tele": 12145, "nama": "adquwhd143"})
print(select_table("user"))

# supabase: Client = create_client(url, key)
# data = supabase.table("user").insert({"id_tele":101214, "nama":"IOAJDAWJD"}).execute()
# assert len(data.get("data", [])) > 0
