import os

from telebot import TeleBot, types
from dotenv import load_dotenv
from dataclasses import dataclass
from lib import checkuser, logfunc, create_conn, convert_to_utc
from random import randint

# Global Variable
load_dotenv()
TOKEN = os.getenv('API')
bot = TeleBot(TOKEN)
global_dict = {}


text_jurusan = []
text_prodi = []

dict_jurusan = {}
dict_prodi = {}

def get_jurusan():
    print("Mengambil Data Jurusan")
    with create_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("select * from jurusan")
        data = cursor.fetchall()
        for i in data:
            dict_jurusan[i[0]] = i[1]
            msg = f"{i[0]} {i[1]}"
            text_jurusan.append(msg)


def get_prodi():
    print("Mengambil Data Prodi")
    with create_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("select * from prodi")
        data = cursor.fetchall()
        for i in data:
            dict_prodi[i[0]] = i[1]
            msg = f"{i[0]} {i[1]}"
            text_prodi.append(msg)



@dataclass
class DataPengumu:
    id_peng = randint(1000,9999)
    id_tele = int
    isi = str
    jurusan = int
    prodi = int
    tingkat = int
    tanggal = str

    def getastuple(self):
        id_peng = self.id_peng
        id_tele = self.id_tele
        isi = self.isi
        jurusan = self.jurusan
        prodi = self.prodi
        tingkat = self.tingkat
        tanggal = self.tanggal
        return (id_peng,id_tele,isi,jurusan,prodi,tingkat,tanggal)

    def setfromtuple(self, datatuple : tuple):
        self.id_peng, self.id_tele, self.isi, self.jurusan, self.prodi, self.tingkat, self.tanggal = datatuple


class InsertPengumuman:
    def first_step(self,message):
        chat_id = int(message.chat.id)
        try:
            if not checkuser(chat_id):
                bot.reply_to(message, "Anda bukan admin")
            else:
                msg = bot.reply_to(message, """\
            Silahkan jawab pertanyaan sesuai data diri.\nIsi Pengumuman:
            """)
                bot.register_next_step_handler(msg, self.second_step)
        except Exception as e:
            logfunc("first step", e)

    def second_step(self,message):
        try:
            chat_id = message.chat.id
            isi = message.text
            data = DataPengumu()
            data.id_tele = chat_id
            data.isi = isi
            global_dict[chat_id] = data
            pesan = "\n".join(text_jurusan)
            msg = bot.reply_to(message, f'{pesan}\n\nJurusan: ')
            bot.register_next_step_handler(msg, self.third_step)
        except Exception as e:
            logfunc('nama', e)
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin')

    def third_step(self,message):
        try:
            chat_id = message.chat.id
            jurusan = int(message.text)
            if jurusan not in dict_jurusan:
                msg = bot.send_message(chat_id=chat_id, text="Silahkan isi sesuai id jurusan")
                bot.register_next_step_handler(msg, self.third_step)
            else:
                data = global_dict[chat_id]
                data.jurusan = jurusan
                pesan = "\n".join(text_prodi)
                msg = bot.reply_to(message, f'{pesan}\n\nProdi : ')
                bot.register_next_step_handler(msg, self.forth_step)
        except Exception as e:
            msg = bot.send_message(chat_id=chat_id, text="Silahkan isi sesuai input")
            bot.register_next_step_handler(msg, self.third_step)
            logfunc("3Rd step Pengumuman", e)

    def forth_step(self, message):
        try:
            chat_id = message.chat.id
            prodi = int(message.text)
            if prodi not in dict_prodi:
                msg = bot.send_message(chat_id=chat_id, text="Silahkan isi sesuai id Prodi")
                bot.register_next_step_handler(msg, self.third_step)
            else:
                data = global_dict[chat_id]
                data.prodi = prodi
                msg = bot.reply_to(message, 'Tingkat : ')
                bot.register_next_step_handler(msg, self.fifth_step)
        except Exception as e:
            msg = bot.send_message(chat_id=chat_id, text="Silahkan isi sesuai input")
            bot.register_next_step_handler(msg, self.forth_step)
            logfunc("5TH Pengumuman", e)

    def fifth_step(self, message):
        try:
            chat_id = message.chat.id
            tingkat = int(message.text)
            if tingkat not in [1,2,3,4]:
                bot.send_message(chat_id=chat_id, text="Tingkat yang tersedia hanya 1 sampai 4")
            else:
                data = global_dict[chat_id]
                data.tingkat = tingkat
                msg = bot.send_message(chat_id, "Waktu dengan format (DD/MM/YYYY HH:MM) :")
                bot.register_next_step_handler(msg, self.six_step)
        except Exception as e:
            msg = bot.send_message(chat_id=chat_id, text="Silahkan masukkan sesuai input")
            bot.register_next_step_handler(msg, self.fifth_step)
            logfunc("FIFTH_STEP_DATE", e)


    def six_step(self, message):
        try:
            chat_id = message.chat.id
            tanggal = convert_to_utc(message.text)
            data = global_dict[chat_id]
            data.tanggal = tanggal
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('ya', 'tidak')
            msg = bot.reply_to(message, f'Date-time (UTC) : {data.tanggal}\nJurusan : {data.jurusan}\n'
                                        f'Prodi : {data.prodi}\nTingkat : {data.tingkat}\nIsi: {data.isi}\n', reply_markup=markup)
            bot.register_next_step_handler(msg, self.commit_to_database)
        except Exception as e:
            logfunc('commit database', e)
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin terjadi error silahkan lapor ke admin')
            msg = bot.reply_to(message, "Silahkan masukkan sesuai format (DD/MM/YYYY HH:MM)")
            bot.register_next_step_handler(msg, self.six_step)

    def commit_to_database(self,message):
        try:
            chat_id = message.chat.id
            keputusan = message.text
            user = global_dict[chat_id]
            if (keputusan == u'ya'):
                insert = "INSERT INTO isi_pengumuman VALUES (%s,%s,%s,%s,%s,%s,%s)"
                val = user.getastuple()
                try:
                    with create_conn() as conn:
                        cursor = conn.cursor()
                        cursor.execute(insert, val)
                        conn.close()
                    bot.send_message(chat_id, "ok data sudah terinput")
                except Exception as e:
                    bot.send_message(chat_id, "terjadi error silahkan ulang kembali")
                    logfunc('commit database', e)
            else:
                msg = bot.send_message(chat_id, "Silahkan tekan -> /daftar untuk melakukan pendaftaran ulang")
                bot.register_next_step_handler(msg, self.first_step)
            # remove used object at user_dict
            del global_dict[chat_id]
        except Exception as e:
            logfunc('commit database', e)

class ListPengumuman:
    def send_list(self, message):
        chat_id = message.chat.id
        try:
            if checkuser(chat_id):
                with create_conn() as conn:
                    cursor = conn.cursor()
                    query = "SELECT isi_pengumuman.id_pengumuman, isi_pengumuman.isi, jurusan.nama_jur, prodi.nama_prod, isi_pengumuman.tingkat, user.nama, isi_pengumuman.tanggal " \
                            "FROM isi_pengumuman " \
                            "INNER JOIN jurusan ON isi_pengumuman.jurusan = jurusan.id_jur " \
                            "INNER JOIN prodi ON isi_pengumuman.prodi=prodi.id_prodi " \
                            "INNER JOIN user ON isi_pengumuman.id_user = user.id_tele"
                    cursor.execute(query)
                    list_data = cursor.fetchall()
                    bot.send_message(chat_id,"Sedang mengambil data")
                    conn.close()
                    for data in list_data:
                        id_pengumuman, isi, nama_jur, prodi,tingkat, nama, tanggal = data
                        text = f"Nama Penulis : {nama}\nTanggal Pengingat : {tanggal}\nID Pengumuman: {id_pengumuman}\nJurusan : {nama_jur}\n" \
                               f"Prodi : {prodi}\nTingkat : {tingkat}\nIsi : \n{isi}\n"
                        bot.send_message(chat_id, text)
            else:
                bot.reply_to(message, "Anda Bukan Admin")
        except Exception as e:
            logfunc("info pengumuman", e)

class DeletePengumuman:
    def deletePengumuman(self, message):
        chat_id = message.chat.id
        text = message.text
        try:
            if checkuser(chat_id):
                msg = bot.send_message(chat_id, text="Kirimkan ID pengumuman yang ingin dihapus : ")
                bot.register_next_step_handler(msg, self.getPengumuman)
            else:
                bot.send_message(chat_id, "Anda Bukan Admin")
        except Exception as e:
            logfunc("delete error", e)

    def getPengumuman(self, message):
        try:
            chat_id = message.chat.id
            user = DataPengumu()
            id_pengumuman = int(message.text)
            user.id_peng = id_pengumuman
            global_dict[chat_id] = user
            with create_conn() as conn:
                cursor = conn.cursor()
                query = "SELECT isi_pengumuman.id_pengumuman, isi_pengumuman.isi, jurusan.nama_jur, prodi.nama_prod, isi_pengumuman.tingkat, user.nama, isi_pengumuman.tanggal " \
                        "FROM isi_pengumuman " \
                        "INNER JOIN jurusan ON isi_pengumuman.jurusan = jurusan.id_jur " \
                        "INNER JOIN prodi ON isi_pengumuman.prodi=prodi.id_prodi " \
                        "INNER JOIN user ON isi_pengumuman.id_user = user.id_tele " \
                        f"WHERE isi_pengumuman.id_pengumuman = {id_pengumuman}"
                cursor.execute(query)
                data = cursor.fetchone()
                if data is not None:
                    id_pengumuman, isi, nama_jur, prodi, tingkat, nama, tanggal = data
                    text = f"Nama Penulis : {nama}\nTanggal Pengingat : {tanggal}\nID Pengumuman: {id_pengumuman}\nJurusan : {nama_jur}\n" \
                            f"Prodi : {prodi}\nTingkat : {tingkat}\nIsi : \n{isi}\n\n" \
                            f"Akan Dihapus?"
                    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
                    markup.add('ya', 'tidak')
                    msg = bot.send_message(chat_id,text, reply_markup=markup)
                    bot.register_next_step_handler(msg, self.commit_database)
                else:
                    bot.send_message(chat_id, "404 : data not found")
        except Exception as e:
            logfunc("Del GetPengumuman", e)

    def commit_database(self, message):
        try:
            chat_id = message.chat.id
            keputusan = message.text
            user = global_dict[chat_id]
            if (keputusan == u'ya'):
                insert = f"DELETE FROM isi_pengumuman WHERE id_pengumuman = {user.id_peng}"
                with create_conn() as conn:
                    cursor = conn.cursor()
                    cursor.execute(insert)
                    conn.close()
                bot.send_message(chat_id, "ok data sudah dihapus")
            else:
                msg = bot.send_message(chat_id, "OK")
            # remove used object at global_dict
            del global_dict[chat_id]
        except Exception as e:
            logfunc('commit database', e)
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin terjadi error silahkan lapor ke admin')

 # // TODO :
# membuat handler update dengan memasukkan data fetch ke dalam class DataPengu
# Kemudian membuat step by step untuk mengupdate data
# ketika balasan dari user = 0 maka data didalam class tidak akan diubah
# mengupdate data dengan query update dengan value yang diambil dari kelas DataPengu
class UpdatePengumuman:
    def first_step(self, message):
        chat_id = int(message.chat.id)
        try:
            if not checkuser(chat_id):
                bot.reply_to(message, "Anda bukan admin")
            else:
                msg = bot.reply_to(message, """\
             Masukkan ID pengumuman yang ingin di Edit:
             """)
                bot.register_next_step_handler(msg, self.second_step)
        except Exception as e:
            logfunc("first step", e)

    def second_step(self, message):
        try:
            chat_id = message.chat.id
            text = message.text
            user = DataPengumu()
            with create_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM isi_pengumuman WHERE id_pengumuman = {text}")
                data = cursor.fetchone()
                user.setfromtuple(data)

            global_dict[chat_id] = user
            bot.send_message(chat_id, f"Isi Pengumuman : {user.isi}")
            msg = bot.reply_to(message, 'Isi yang mau diganti : ')
            bot.register_next_step_handler(msg, self.third_step)
        except Exception as e:
            logfunc('nama', e)
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin')

    def third_step(self, message):
        try:
            chat_id = message.chat.id
            isi = message.text
            data = global_dict[chat_id]
            if str(isi).lower() in ["skip", "lewat"]:
                pass
            else:
                data.isi = isi
            bot.send_message(chat_id, f"Jurusan : {data.jurusan}")
            msg = bot.reply_to(message, 'Jurusan yang ingin diganti : ')
            bot.register_next_step_handler(msg, self.forth_step)
        except Exception as e:
            logfunc("3Rd step Pengumuman", e)

    def forth_step(self, message):
        try:
            chat_id = message.chat.id
            jurusan = message.text
            data = global_dict[chat_id]
            if str(jurusan).lower() in ["skip", "lewat"]:
                bot.send_message(chat_id, f"Prodi : {data.prodi}")
                msg = bot.reply_to(message, 'Prodi yang ingin diganti : ')
                bot.register_next_step_handler(msg, self.fifth_step)
            elif int(jurusan) not in dict_jurusan:
                pesan = "\n".join(text_jurusan)
                msg = bot.send_message(chat_id=chat_id, text=f"{pesan}\n\nTidak sesuai jurusan")
                bot.register_next_step_handler(msg, self.forth_step)
            else:
                data.jurusan = jurusan
                bot.send_message(chat_id, f"Prodi : {data.prodi}")
                msg = bot.reply_to(message, 'Prodi yang ingin diganti : ')
                bot.register_next_step_handler(msg, self.fifth_step)
        except Exception as e:
            logfunc("5TH Pengumuman", e)
            bot.register_next_step_handler(bot.reply_to(message, "Silahkan Isi Kembali"), self.forth_step)

    def fifth_step(self, message):
        try:
            chat_id = message.chat.id
            prodi = message.text
            data = global_dict[chat_id]
            if str(prodi).lower() in ["skip", "lewat"]:
                bot.send_message(chat_id, f"Tingkat : {data.tingkat}")
                msg = bot.reply_to(message, 'Tingkat yang ingin diganti : ')
                bot.register_next_step_handler(msg, self.six_step)
            elif int(prodi) not in dict_prodi:
                pesan = "\n".join(text_prodi)
                msg = bot.send_message(chat_id=chat_id, text=f"{pesan}\n\n Tidak sesuai Prodi")
                bot.register_next_step_handler(msg, self.fifth_step)
            else:
                data.prodi = prodi
                bot.send_message(chat_id, f"Tingkat : {data.tingkat}")
                msg = bot.reply_to(message, 'Tingkat yang ingin diganti : ')
                bot.register_next_step_handler(msg, self.six_step)
        except Exception as e:
            logfunc("5TH Pengumuman", e)
            bot.register_next_step_handler(bot.reply_to(message, "Silahkan Isi Kembali"), self.fifth_step)

    def six_step(self, message):
        try:
            chat_id = message.chat.id
            tingkat = message.text
            data = global_dict[chat_id]
            if str(tingkat).lower() in ["skip", "lewat"]:
                bot.send_message(chat_id, f"Tanggal : {data.tanggal}")
                msg = bot.reply_to(message, 'Tanggal yang ingin diganti : ')
                bot.register_next_step_handler(msg, self.seven_step)
            elif int(tingkat) not in [1,2,3,4]:
                msg = bot.send_message(chat_id=chat_id, text=f"Tingkat yang tersedia hanya 1 sampai 4")
                bot.register_next_step_handler(msg, self.six_step)
            else:
                data.tingkat = tingkat
                bot.send_message(chat_id, f"Tanggal : {data.tanggal}")
                msg = bot.reply_to(message, 'Tanggal yang ingin diganti : ')
                bot.register_next_step_handler(msg, self.seven_step)
        except Exception as e:
            logfunc("5TH Pengumuman", e)
            bot.register_next_step_handler(bot.reply_to(message, "Silahkan Isi Kembali"), self.six_step)

    def seven_step(self, message):
        try:
            chat_id = message.chat.id
            tanggal = message.text
            data = global_dict[chat_id]
            if str(tanggal).lower() in ["skip", "lewat"]:
                pass
            else:
                tanggal = convert_to_utc(tanggal)
                data.tanggal = tanggal
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('ya', 'tidak')
            msg = bot.reply_to(message, f'Date-time (UTC) : {data.tanggal}\nJurusan : {data.jurusan}\n'
                                        f'Prodi : {data.prodi}\nTingkat : {data.tingkat}\nIsi: {data.isi}\n',
                               reply_markup=markup)
            bot.register_next_step_handler(msg, self.commit_to_database)
        except Exception as e:
            logfunc('commit database', e)
            msg = bot.reply_to(message, 'Format tidak sesuai, silahkan isi kembali')
            bot.register_next_step_handler(msg, self.seven_step)

    def commit_to_database(self, message):
        try:
            chat_id = message.chat.id
            keputusan = message.text
            user = global_dict[chat_id]
            # id_peng = randint(1000, 9999)
            # id_tele = int
            # isi = str
            # jurusan = int
            # prodi = int
            # tingkat = int
            # tanggal = str
            # TODO:
            #   fix QUERY FOR UPDATE
            #
            if (keputusan == u'ya'):
                # insert = "UPDATE isi_pengumuman SET " \
                #          f"isi = {user.isi}, jurusan = {user.jurusan}, " \
                #          f"prodi = {user.prodi}, tingkat = {user.tingkat}," \
                #          f"tanggal = {user.tanggal} WHERE id_pengumuman = {user.id_peng}"
                insert = f"UPDATE isi_pengumuman SET isi=%s," \
                         f"jurusan=%s,prodi=%s,tingkat=%s,tanggal=%s " \
                         f"WHERE id_pengumuman =%s"
                val = (user.isi, user.jurusan, user.prodi, user.tingkat, str(user.tanggal), user.id_peng)
                try:
                    with create_conn() as conn:
                        cursor = conn.cursor()
                        cursor.execute(insert, val)
                        conn.close()
                    bot.send_message(chat_id, "ok data sudah terupdate")
                except Exception as e:
                    bot.send_message(chat_id, "terjadi error silahkan ulang kembali")
                    logfunc('commit database', e)
            else:
                bot.send_message(chat_id, "Silahkan tekan -> /update untuk melakukan update data")
            # remove used object at user_dict
            del global_dict[chat_id]
        except Exception as e:
            logfunc('commit database', e)
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin terjadi error silahkan lapor ke admin')

list_pengu = ListPengumuman()
pengu = InsertPengumuman()
del_pengu = DeletePengumuman()
up_pengu = UpdatePengumuman()

bot.register_message_handler(pengu.first_step, commands=["start"])
bot.register_message_handler(list_pengu.send_list, commands=["list"])
bot.register_message_handler(del_pengu.deletePengumuman, commands=["del"])
bot.register_message_handler(up_pengu.first_step, commands=["update"])


if __name__=='__main__':
    get_prodi()
    get_jurusan()
    print("BOT IS BERLARI")
    bot.polling()

