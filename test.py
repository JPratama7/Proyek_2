from mysql import connector
import os
from datetime import datetime
from lib import create_conn

# host = os.environ.get("HOST")
# user = "root"
# password = os.environ.get("PASSWORD")
# database = "pengumuman"
#
# conn = connector.connect(host=host, user=user, password=password, database=database, autocommit=True)
# cursor = conn.cursor()
#
# id_tele = int(1201809639)
# query = f"SELECT * FROM user WHERE id_tele={id_tele}"
#
# data = cursor.execute(query)

# date_time_str = "18/09/2020 01:55:19"
# print(type(date_time_str))
#
# date_time_obj = datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S')
#
#
# print ("The type of the date is now",  type(date_time_obj))
# print ("The date is", date_time_obj)
dict_jurusan = {}

print("Mengambil ID Jurusan")
with create_conn() as conn:
    cursor = conn.cursor()
    cursor.execute("select * from jurusan")
    data = cursor.fetchall()
    for i in data:
        dict_jurusan[i[0]] = i[1]

print(dict_jurusan)
k = 1
if k in dict_jurusan:
    print("bernar")
else:
    print("c")
