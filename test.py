from mysql import connector
import os

host = os.environ.get("HOST")
user = "root"
password = os.environ.get("PASSWORD")
database = "pengumuman"

conn = connector.connect(host=host, user=user, password=password, database=database, autocommit=True)
cursor = conn.cursor()

id_tele = int(1201809639)
query = f"SELECT * FROM user WHERE id_tele={id_tele}"

data = cursor.execute(query)
print(data)