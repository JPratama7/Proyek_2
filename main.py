import os

from telebot import TeleBot, types
from dotenv import load_dotenv
from dataclasses import dataclass
from lib import checkuser, logfunc, create_conn, converttodate
from random import randint

# Global Variable
load_dotenv()
TOKEN = os.getenv('API')
bot = TeleBot(TOKEN)

global_dict = {}

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


class Pengumuman:
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
            msg = bot.reply_to(message, 'Jurusan: ')
            bot.register_next_step_handler(msg, self.third_step)
        except Exception as e:
            logfunc('nama', e)
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin')

    def third_step(self,message):
        try:
            chat_id = message.chat.id
            jurusan = message.text
            data = global_dict[chat_id]
            data.jurusan = jurusan
            msg = bot.reply_to(message, 'Prodi : ')
            bot.register_next_step_handler(msg, self.forth_step)
        except Exception as e:
            logfunc("3Rd step Pengumuman", e)

    def forth_step(self, message):
        try:
            chat_id = message.chat.id
            prodi = message.text
            data = global_dict[chat_id]
            data.prodi = prodi
            msg = bot.reply_to(message, 'Tingkat : ')
            bot.register_next_step_handler(msg, self.fifth_step)
        except Exception as e:
            logfunc("5TH Pengumuman", e)

    def fifth_step(self, message):
        try:
            chat_id = message.chat.id
            tingkat = message.text
            data = global_dict[chat_id]
            data.tingkat = tingkat
            msg = bot.send_message(chat_id, "Waktu dengan format (DD/MM/YYYY HH:MM) :")
            bot.register_next_step_handler(msg, self.six_step)
        except Exception as e:
            logfunc("FIFTH_STEP_DATE", e)


    def six_step(self, message):
        try:
            chat_id = message.chat.id
            tanggal = converttodate(message.text)
            data = global_dict[chat_id]
            data.tanggal = tanggal
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('ya', 'tidak')
            msg = bot.reply_to(message, f'Date-Time : {data.tanggal}\nJurusan : {data.jurusan}\n'
                                        f'Prodi : {data.prodi}\nTingkat : {data.tingkat}\nIsi: {data.isi}\n', reply_markup=markup)
            bot.register_next_step_handler(msg, self.commit_to_database)
        except Exception as e:
            logfunc('commit database', e)
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin terjadi error silahkan lapor ke admin')

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
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin terjadi error silahkan lapor ke admin')

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
        chat_id = message.chat.id
        user = DataPengumu()
        id_pengumuman = int(message.text)
        user.id_peng = id_pengumuman
        global_dict[chat_id] = user
        try:
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

# TODO :
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
        chat_id = message.chat.id
        text = message.text
        try:
            with create_conn() as conn:
                cursor = conn.cursor()
                # query =


            chat_id = message.chat.id
            isi = message.text
            data = DataPengumu()
            data.id_tele = chat_id
            data.isi = isi
            global_dict[chat_id] = data
            msg = bot.reply_to(message, 'Jurusan: ')
            bot.register_next_step_handler(msg, self.third_step)
        except Exception as e:
            logfunc('nama', e)
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin')

    def third_step(self, message):
        try:
            chat_id = message.chat.id
            jurusan = message.text
            data = global_dict[chat_id]
            data.jurusan = jurusan
            msg = bot.reply_to(message, 'Prodi : ')
            bot.register_next_step_handler(msg, self.forth_step)
        except Exception as e:
            logfunc("3Rd step Pengumuman", e)

    def forth_step(self, message):
        try:
            chat_id = message.chat.id
            prodi = message.text
            data = global_dict[chat_id]
            data.prodi = prodi
            msg = bot.reply_to(message, 'Tingkat : ')
            bot.register_next_step_handler(msg, self.fifth_step)
        except Exception as e:
            logfunc("5TH Pengumuman", e)

    def fifth_step(self, message):
        try:
            chat_id = message.chat.id
            tingkat = message.text
            data = global_dict[chat_id]
            data.tingkat = tingkat
            msg = bot.send_message(chat_id, "Waktu dengan format (DD/MM/YYYY HH:MM) :")
            bot.register_next_step_handler(msg, self.six_step)
        except Exception as e:
            logfunc("FIFTH_STEP_DATE", e)

    def six_step(self, message):
        try:
            chat_id = message.chat.id
            tanggal = converttodate(message.text)
            data = global_dict[chat_id]
            data.tanggal = tanggal
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('ya', 'tidak')
            msg = bot.reply_to(message, f'Date-Time : {data.tanggal}\nJurusan : {data.jurusan}\n'
                                        f'Prodi : {data.prodi}\nTingkat : {data.tingkat}\nIsi: {data.isi}\n',
                               reply_markup=markup)
            bot.register_next_step_handler(msg, self.commit_to_database)
        except Exception as e:
            logfunc('commit database', e)
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin terjadi error silahkan lapor ke admin')

    def commit_to_database(self, message):
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
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin terjadi error silahkan lapor ke admin')

list_pengu = ListPengumuman()
pengu = Pengumuman()
del_pengu = DeletePengumuman()

bot.register_message_handler(pengu.first_step, commands=["start"])
bot.register_message_handler(list_pengu.send_list, commands=["list"])
bot.register_message_handler(del_pengu.deletePengumuman, commands=["del"])


print("BOT IS BERLARI")
bot.infinity_polling()