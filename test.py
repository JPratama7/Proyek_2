from mysql import connector
import os
from datetime import datetime

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

date_time_str = "18/09/2020 01:55:19"
print(type(date_time_str))

date_time_obj = datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S')


print ("The type of the date is now",  type(date_time_obj))
print ("The date is", date_time_obj)