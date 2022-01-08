import os
import re

from telebot import TeleBot, types
from dotenv import load_dotenv
from dataclasses import dataclass
from lib import checkuser, logfunc, create_conn, convert_to_utc, checksiswa, convert_utc_to_usertz,\
    convert_to_utc_from_user
from random import randint
from mysql.connector import Error

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
    id_peng = randint(1000, 9999)
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
        return (id_peng, id_tele, isi, jurusan, prodi, tingkat, tanggal)

    def setfromtuple(self, datatuple: tuple):
        self.id_peng, self.id_tele, self.isi, self.jurusan, self.prodi, self.tingkat, self.tanggal = datatuple


@dataclass
class User:
    id_tele = int
    nama = str
    jurusan = int
    prodi = int
    tingkat = int

    def getastuple(self):
        id_tele = self.id_tele
        nama = self.nama
        jurusan = self.jurusan
        prodi = self.prodi
        tingkat = self.tingkat
        return (id_tele, nama, jurusan, prodi, tingkat)

    def setfromtuple(self, datatuple: tuple):
        self.id_tele, self.jurusan, self.prodi, self.tingkat = datatuple


class InsertPengumuman:
    def first_step(self, message):
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

    def second_step(self, message):
        try:
            chat_id = message.chat.id
            isi = message.text
            data = DataPengumu()
            data.id_tele = chat_id
            data.isi = isi
            global_dict[chat_id] = data
            pesan = "\n".join(text_jurusan)
            bot.register_next_step_handler(
                bot.send_message(chat_id, f'{pesan}\n\nJurusan: '), self.third_step
            )
        except Exception as e:
            logfunc('nama', e)
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin')

    def third_step(self, message):
        chat_id = message.chat.id
        try:
            jurusan = int(message.text) if message.text.isdigit() else bot.register_next_step_handler(
                bot.send_message(chat_id, "Input salah, silahkan input angka"), self.third_step
            )
            if jurusan not in dict_jurusan:
                bot.register_next_step_handler(
                    bot.send_message(chat_id=chat_id, text="Silahkan isi sesuai id jurusan"),
                    self.third_step
                )
            else:
                data = global_dict[chat_id]
                data.jurusan = jurusan
                pesan = "\n".join(text_prodi)
                bot.register_next_step_handler(
                    bot.send_message(chat_id, f'{pesan}\n\nProdi : '), self.forth_step
                )
        except Exception as e:
            del global_dict[chat_id]
            logfunc("3Rd step Pengumuman", e)

    def forth_step(self, message):
        chat_id = message.chat.id
        try:
            prodi = int(message.text) if message.text.isdigit() else bot.register_next_step_handler(
                bot.send_message(chat_id, "Input salah, silahkan input angka"), self.forth_step
            )
            if prodi not in dict_prodi:
                bot.register_next_step_handler(
                    bot.send_message(chat_id=chat_id, text="Silahkan isi sesuai id Prodi"), self.forth_step
                )
            else:
                data = global_dict[chat_id]
                data.prodi = prodi
                bot.register_next_step_handler(
                    bot.send_message(chat_id, "Tingkat : "), self.fifth_step
                )
        except Exception as e:
            del global_dict[chat_id]
            logfunc("5TH Pengumuman", e)
            bot.send_message(chat_id, "oooops terjadi error silahkan lapor ke admin")

    def fifth_step(self, message):
        chat_id = message.chat.id
        try:
            tingkat = int(message.text) if message.text.isdigit() else bot.register_next_step_handler(
                bot.send_message(chat_id, "Input salah, silahkan input angka"), self.fifth_step
            )
            if tingkat not in [1, 2, 3, 4]:
                bot.register_next_step_handler(
                    bot.send_message(chat_id=chat_id,text="Tingkat yang tersedia hanya 1 sampai 4")
                    , self.fifth_step)
            else:
                data = global_dict[chat_id]
                data.tingkat = tingkat
                bot.register_next_step_handler(
                    bot.send_message(chat_id, "Waktu dengan format (DD/MM/YYYY HH:MM) :"),
                    self.six_step
                )
        except Exception as e:
            del global_dict[chat_id]
            logfunc("FIFTH_STEP_DATE", e)
            bot.send_message(chat_id, "oooops terjadi error silahkan lapor ke admin")

    def six_step(self, message):
        chat_id = message.chat.id
        try:
            tanggal = convert_to_utc(message.text)
            data = global_dict[chat_id]
            data.tanggal = tanggal
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('ya', 'tidak')
            bot.register_next_step_handler(
                bot.reply_to(message, f'Date-time (UTC) : {data.tanggal}\nJurusan : {data.jurusan}\n'
                                      f'Prodi : {data.prodi}\nTingkat : {data.tingkat}\nIsi: {data.isi}\n',
                             reply_markup=markup),
                self.commit_to_database
            )
        except ValueError:
            bot.register_next_step_handler(
                bot.send_message(chat_id, "Silahkan masukkan sesuai format (DD/MM/YYYY HH:MM)"), self.six_step
            )
        except Exception as e:
            logfunc('commit database', e)
            bot.send_message(chat_id, 'oooops terjadi error, silahkan ulang kembali')

    def commit_to_database(self, message):
        chat_id = message.chat.id
        keputusan = message.text
        try:
            user = global_dict[chat_id]
            if (keputusan == 'ya'):
                insert = "INSERT INTO isi_pengumuman VALUES (%s,%s,%s,%s,%s,%s,%s)"
                val = user.getastuple()
                with create_conn() as conn:
                    cursor = conn.cursor()
                    cursor.execute(insert, val)
                bot.send_message(chat_id, "ok data sudah terinput")
            else:
                bot.register_next_step_handler(
                    bot.send_message(chat_id, "Silahkan tekan -> /insert untuk melakukan pendaftaran ulang"),
                    self.first_step
                )
            # remove used object at user_dict
            del global_dict[chat_id]
        except Exception as e:
            del global_dict[chat_id]
            logfunc('commit database', e)
            bot.send_message(chat_id, 'oooops terjadi error, silahkan ulang kembali')



class ListPengumuman:
    def send_list(self, message):
        chat_id = message.chat.id
        try:
            if checkuser(chat_id):
                with create_conn() as conn:
                    cursor = conn.cursor()
                    query = "SELECT isi_pengumuman.id_pengumuman, isi_pengumuman.isi, jurusan.nama_jur, prodi.nama_prod," \
                            " isi_pengumuman.tingkat, user.nama, isi_pengumuman.tanggal " \
                            "FROM isi_pengumuman " \
                            "INNER JOIN jurusan ON isi_pengumuman.jurusan = jurusan.id_jur " \
                            "INNER JOIN prodi ON isi_pengumuman.prodi=prodi.id_prodi " \
                            "INNER JOIN user ON isi_pengumuman.id_user = user.id_tele"
                    cursor.execute(query)
                    list_data = cursor.fetchall()
                    bot.send_message(chat_id, "Sedang mengambil data")
                    for data in list_data:
                        id_pengumuman, isi, nama_jur, prodi, tingkat, nama, tanggal = data
                        text = f"Nama Penulis : {nama}\nTanggal Pengingat : {tanggal}\nID Pengumuman: {id_pengumuman}\nJurusan : {nama_jur}\n" \
                               f"Prodi : {prodi}\nTingkat : {tingkat}\nIsi : \n{isi}\n"
                        bot.send_message(chat_id, text)
            else:
                bot.reply_to(message, "Anda Bukan Admin")
        except Exception as e:
            logfunc("info pengumuman", e)
            bot.send_message(chat_id, 'oooops terjadi error, silahkan ulang kembali')


class DeletePengumuman:
    def deletePengumuman(self, message):
        chat_id = message.chat.id
        list = ListPengumuman()
        list.send_list(message)
        try:
            if checkuser(chat_id):
                bot.register_next_step_handler(
                    bot.send_message(chat_id, text="Kirimkan ID pengumuman yang ingin dihapus : "),
                    self.getPengumuman)
            else:
                bot.send_message(chat_id, "Anda Bukan Admin")
        except Exception as e:
            logfunc("delete error", e)
            bot.send_message(chat_id, 'oooops terjadi error, silahkan ulang kembali')


    def getPengumuman(self, message):
        chat_id = message.chat.id
        try:
            user = DataPengumu()
            id_pengumuman = int(message.text) if message.text.isdigit() else bot.register_next_step_handler(
                bot.send_message(chat_id, "Silahkan masukkan ID pengumuman yang ingin dihapus"), self.getPengumuman
            )
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
                    bot.register_next_step_handler(
                        bot.send_message(chat_id, text, reply_markup=markup),
                        self.commit_database)
                else:
                    bot.send_message(chat_id, "404 : data not found")
        except Exception as e:
            del global_dict[chat_id]
            logfunc("Del GetPengumuman", e)
            bot.send_message(chat_id, 'oooops terjadi error, silahkan ulang kembali')


    def commit_database(self, message):
        chat_id = message.chat.id
        keputusan = message.text
        try:
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
            del global_dict[chat_id]
            logfunc('commit database', e)
            bot.send_message(chat_id, 'oooops terjadi error, silahkan ulang kembali')


class UpdatePengumuman:
    def first_step(self, message):
        chat_id = int(message.chat.id)
        list = ListPengumuman()
        list.send_list(message)
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
            bot.send_message(chat_id, 'oooops terjadi error, silahkan ulang kembali')


    def second_step(self, message):
        chat_id = message.chat.id
        try:
            text = int(message.text) if message.text.isdigit() else bot.register_next_step_handler(
                bot.send_message(
                    chat_id, "ID pengumuman harus angka"
                ), self.second_step
            )
            user = DataPengumu()
            with create_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM isi_pengumuman WHERE id_pengumuman = {text}")
                data = cursor.fetchone()
                if data is None:
                    bot.send_message(chat_id, "Pengumuman tidak ditemukan")
                else:
                    user.setfromtuple(data)
                    global_dict[chat_id] = user
                    bot.send_message(chat_id, f"Isi Pengumuman : {user.isi}")
                    bot.register_next_step_handler(
                        bot.reply_to(message, 'Isi yang mau diganti (SKIP untuk melewati): '),
                        self.third_step)
        except Exception as e:
            logfunc('nama', e)
            bot.send_message(chat_id, 'oooops terjadi error, silahkan ulang kembali')


    def third_step(self, message):
        chat_id = message.chat.id
        try:
            isi = message.text if not message.text.isdigit() else str(message.text).lower()
            data = global_dict[chat_id]
            if isi in ["skip", "lewat"]:
                pass
            else:
                data.isi = isi
            bot.send_message(chat_id, f"Jurusan : {data.jurusan}")
            bot.register_next_step_handler(
                bot.reply_to(message, 'Jurusan yang ingin diganti ("skip" untuk melewati): '),
                self.forth_step)
        except Exception as e:
            del global_dict[chat_id]
            logfunc("3Rd step Pengumuman", e)
            bot.send_message(chat_id, 'oooops terjadi error, silahkan ulang kembali')


    def forth_step(self, message):
        chat_id = message.chat.id
        try:
            jurusan = int(message.text) if message.text.isdigit() else str(message.text).lower()
            data = global_dict[chat_id]
            if jurusan in ["skip", "lewat"]:
                bot.send_message(chat_id, f"Prodi : {data.prodi}")
                bot.register_next_step_handler(
                    bot.reply_to(message, 'Prodi yang ingin diganti ("skip" untuk melewati): '),
                    self.fifth_step)
            elif jurusan not in dict_jurusan:
                pesan = "\n".join(text_jurusan)
                bot.register_next_step_handler(
                    bot.send_message(chat_id=chat_id, text=f"{pesan}\n\nTidak sesuai jurusan"),
                    self.forth_step
                )
            else:
                data.jurusan = jurusan
                bot.send_message(chat_id, f"Prodi : {data.prodi}")
                bot.register_next_step_handler(
                    bot.reply_to(message, 'Prodi yang ingin diganti ("skip" untuk melewati): '),
                    self.fifth_step
                )
        except Exception as e:
            del global_dict[chat_id]
            logfunc("5TH Pengumuman", e)
            bot.send_message(chat_id, 'oooops terjadi error, silahkan ulang kembali')
            # bot.register_next_step_handler(bot.reply_to(message, "Silahkan Isi Kembali"), self.forth_step)

    def fifth_step(self, message):
        chat_id = message.chat.id
        try:
            prodi = int(message.text) if message.text.isdigit() else str(message.text).lower()
            data = global_dict[chat_id]
            if prodi in ["skip", "lewat"]:
                bot.send_message(chat_id, f"Tingkat : {data.tingkat}")
                bot.register_next_step_handler(
                    bot.send_message(chat_id, 'Tingkat yang ingin diganti ("skip" untuk melewati): '),
                    self.six_step
                )
            elif prodi not in dict_prodi:
                pesan = "\n".join(text_prodi)
                bot.register_next_step_handler(
                    bot.send_message(chat_id=chat_id, text=f"{pesan}\n\n Tidak sesuai Prodi"),
                    self.fifth_step
                )
            else:
                data.prodi = prodi
                bot.send_message(chat_id, f"Tingkat : {data.tingkat}")
                bot.register_next_step_handler(
                    bot.reply_to(message, 'Tingkat yang ingin diganti ("skip" untuk melewati) : '),
                    self.six_step
                )
        except Exception as e:
            logfunc("5TH Pengumuman", e)
            bot.register_next_step_handler(bot.reply_to(message, "Silahkan Isi Kembali"), self.fifth_step)

    def six_step(self, message):
        try:
            chat_id = message.chat.id
            tingkat = int(message.text) if message.text.isdigit() else str(message.text).lower()
            data = global_dict[chat_id]
            if tingkat in ["skip", "lewat"]:
                bot.send_message(chat_id, f"Tanggal : {convert_utc_to_usertz(data.tanggal, 'WIB')}")
                bot.register_next_step_handler(
                    bot.send_message(chat_id, 'Tanggal yang ingin diganti ("skip" untuk melewati) : '),
                    self.seven_step
                )
            elif tingkat not in [1, 2, 3, 4]:
                bot.register_next_step_handler(
                    bot.send_message(chat_id=chat_id, text=f"Tingkat yang tersedia hanya 1 sampai 4 "), self.six_step
                )
            else:
                data.tingkat = tingkat
                bot.send_message(chat_id, f"Tanggal : {data.tanggal}")
                bot.register_next_step_handler(
                    bot.reply_to(message, 'Tanggal yang ingin diganti : '), self.seven_step
                )
        except Exception as e:
            logfunc("5TH Pengumuman", e)
            bot.register_next_step_handler(bot.reply_to(message, "Silahkan Isi Kembali"), self.six_step)

    def seven_step(self, message):
        chat_id = message.chat.id
        try:
            tanggal = str(message.text).lower()
            data = global_dict[chat_id]
            if tanggal in ["skip", "lewat"]:
                pass
            else:
                tanggal = convert_to_utc(tanggal)
                data.tanggal = tanggal
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('ya', 'tidak')
            bot.register_next_step_handler(
                bot.send_message(chat_id, f'Date-time (UTC) : {data.tanggal}\nJurusan : {data.jurusan}\n'
                                      f'Prodi : {data.prodi}\nTingkat : {data.tingkat}\nIsi: {data.isi}\n',
                             reply_markup=markup),
                self.commit_to_database
            )
        except ValueError:
            bot.register_next_step_handler(
                bot.reply_to(message, 'Format tidak sesuai, silahkan isi kembali'), self.seven_step
            )
        except Exception as e:
            logfunc('commit database', e)
            bot.send_message(chat_id, 'Terjadi kesalahan, silahkan coba lagi')

    def commit_to_database(self, message):
        chat_id = message.chat.id
        keputusan = message.text
        try:
            user = global_dict[chat_id]
            if (keputusan == u'ya'):
                insert = f"UPDATE isi_pengumuman SET isi=%s," \
                         f"jurusan=%s,prodi=%s,tingkat=%s,tanggal=%s " \
                         f"WHERE id_pengumuman =%s"
                val = (user.isi, user.jurusan, user.prodi, user.tingkat, str(user.tanggal), user.id_peng)
                with create_conn() as conn:
                    cursor = conn.cursor()
                    cursor.execute(insert, val)
                bot.send_message(chat_id, "ok data sudah terupdate")
            else:
                bot.send_message(chat_id, "Silahkan tekan -> /update untuk melakukan update data")
            # remove used object at user_dict
            del global_dict[chat_id]
        except Exception as e:
            del global_dict[chat_id]
            logfunc('commit database', e)
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin terjadi error silahkan lapor ke admin')


class DaftarUser:
    def get_nama(self,msg):
        chat_id = msg.chat.id
        if checksiswa(chat_id):
            bot.send_message(chat_id, "Anda sudah terdaftar")
        else:
            bot.register_next_step_handler(
                bot.send_message(chat_id, "Silahkan masukkan nama anda"), self.first_step
            )

    def first_step(self, msg):
        chat_id = msg.chat.id
        user = User()
        user.nama = msg.text
        global_dict[chat_id] = user
        try:
            pesan = "\n".join(text_jurusan)
            bot.send_message(chat_id=chat_id, text=f"List jurusan: \n{pesan}")
            bot.register_next_step_handler(
                bot.send_message(chat_id, "Silahkan masukkan jurusan anda anda"), self.second_step
            )
        except Exception as e:
            del global_dict[chat_id]
            logfunc('first step Daftar', e)
            bot.send_message(chat_id, "Terjadi error silahkan ulang kembali")

    def second_step(self, msg):
        chat_id = msg.chat.id
        try:
            text = int(msg.text) if msg.text.isdigit() else bot.register_next_step_handler(
                bot.send_message(chat_id, "Input tidak sesuai, silahkan masukkan kembali"), self.third_step
            )
            user = global_dict[chat_id]
            user.id_tele = chat_id
            if text not in dict_jurusan:
                msg = bot.send_message(chat_id, "\n".join(text_jurusan) +
                                       "\nJurusan tidak ditemukan, silahkan masukkan jurusan anda kembali")
                bot.register_next_step_handler(msg, self.second_step)
            else:
                user.jurusan = text
                global_dict[chat_id] = user
                pesan = "\n".join(text_prodi)
                bot.send_message(chat_id, f"List Prodi :\n{pesan}")
                bot.register_next_step_handler(
                    bot.send_message(chat_id, "Silahkan masukkan prodi anda"), self.third_step
                )
        except Exception as e:
            del global_dict[chat_id]
            logfunc('second step Daftar', e)
            bot.send_message(chat_id, "Terjadi error silahkan ulang kembali")

    def third_step(self, msg):
        chat_id = msg.chat.id
        try:
            text = int(msg.text) if msg.text.isdigit() else bot.register_next_step_handler(
                bot.send_message(chat_id, "Input tidak sesuai, silahkan masukkan kembali"), self.third_step
            )
            if text not in dict_prodi:
                bot.register_next_step_handler(
                    bot.send_message(chat_id,
                                     "\n".join(text_prodi) + "\nInput tidak sesuai, silahkan masukkan kembali"),
                    self.third_step
                )
            else:
                user = global_dict[chat_id]
                user.prodi = text
                bot.register_next_step_handler(
                    bot.send_message(chat_id, "Silahkan masukkan tingkat anda"), self.fourth_step
                )
        except Exception as e:
            del global_dict[chat_id]
            logfunc('third step Daftar', e)
            bot.send_message(chat_id, "Terjadi error silahkan ulang kembali")

    def fourth_step(self, msg):
        chat_id = msg.chat.id
        try:
            text = int(msg.text) if msg.text.isdigit() else bot.register_next_step_handler(
                bot.send_message(chat_id, "Input tidak sesuai, silahkan masukkan kembali"), self.third_step
            )
            user = global_dict[chat_id]
            if text in range(1, 4):
                user.tingkat = text
                data = user.getastuple()
                bot.send_message(chat_id,f"Nama : {data[1]}\n"
                                         f"Tingkat : {data[4]}\n"
                                         f"Jurusan : {data[2]}\n"
                                         f"Prodi : {data[3]}\n")
                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
                markup.add('ya', 'tidak')
                bot.register_next_step_handler(
                    bot.send_message(chat_id, "Apakah anda ingin menambahkan data? (ya/tidak)", reply_markup=markup),
                    self.commit_database_step
                )
            else:
                bot.send_message(chat_id, "Input tingkat hanya 1 sampai 4")
                bot.register_next_step_handler(
                    bot.send_message(chat_id, "Silahkan masukkan tingkat anda"), self.fourth_step
                )
        except Exception as e:
            del global_dict[chat_id]
            logfunc('fourth step Daftar', e)
            bot.send_message(chat_id, "Terjadi error silahkan ulang kembali")

    def commit_database_step(self, msg):
        chat_id = msg.chat.id
        try:
            text = msg.text
            if text == 'ya':
                user = global_dict[chat_id]
                insert = "INSERT INTO `siswa`(`id_tele`, `nama`, `jurusan`, `prodi`, `tingkat`) VALUES (%s, %s, %s, %s, %s)"
                val = user.getastuple()
                with create_conn() as conn:
                    cursor = conn.cursor()
                    cursor.execute(insert, val)
                    conn.commit()
                    bot.send_message(chat_id, "Data anda telah tersimpan")
            else:
                bot.send_message(chat_id, "Terima kasih telah menggunakan layanan kami")
        except Exception as e:
            del global_dict[chat_id]
            logfunc('commit database', e)
            bot.send_message(chat_id, "Terjadi error silahkan ulang kembali")


class Help:
    def help(self, msg):
        chat_id = msg.chat.id
        pesan = """
        
        *Bantuan*
Untuk melakukan pendaftaran siswa silahkan ketik /daftar
Untuk menambahkan agenda silahkan ketik /agenda tambahkan
Untuk menghapus agenda silahkan ketik /agenda hapus
Untuk menampilkan agenda silahkan ketik /agenda list
        
        *Bantuan (Admin Only)*
Untuk melihat daftar pengumuman silahkan ketik /list
Untuk menghapus pengumuman silahkan ketik /del
Untuk memasukkan pengumuman silahkan ketik /insert
Untuk mengupdat/mengubah pengumuman silahkan ketik /update
        
Note:
        Perhatikan keyword yang ditulis
        """
        bot.send_message(chat_id, pesan, parse_mode='Markdown')

class Agenda:

    def router(self, msg):
        chat_id = msg.chat.id
        text = msg.text.lower().split()
        if len(text) > 1:
            if text[1] == 'tambah':
                self.tambah_agenda(msg)
            elif text[1] == 'hapus':
                self.remove_agenda(msg)
            elif text[1] == 'list':
                self.list_agenda(msg)
            else:
                bot.send_message(chat_id, "Perintah tidak dikenali")
        else:
            bot.send_message(chat_id, "WHY PERINTAHNYA KURANG")

    def tambah_agenda(self, msg):
        chat_id = msg.chat.id
        text = msg.text.split(' ')
        text = text[2:]
        text = ' '.join(text)
        result = re.split('agendanya', text)
        if len(result) > 1:
            list = [s.strip() for s in result]
            agenda = list[1]
            waktu = convert_to_utc_from_user(list[0])
            with create_conn() as conn:
                cursor = conn.cursor()
                query = "INSERT INTO reminder_user VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (randint(1, 9999), chat_id, agenda, waktu))
                conn.commit()
                bot.send_message(chat_id, "Agenda telah ditambahkan")
        else:
            bot.send_message(chat_id, "Format agenda tidak sesuai\n"
                                      "Silahkan mengikuti contoh dibawah ini\n"
                                      "/agenda 6 jan 21 17:21 agendanya Mabar Valorant")

    def list_agenda(self, msg):
        chat_id = int(msg.chat.id)
        with create_conn() as conn:
            cursor = conn.cursor()
            query = f"SELECT isi_reminder, waktu, id_reminder FROM reminder_user WHERE id_telegram = {chat_id}"
            cursor.execute(query)
            result = cursor.fetchall()
            if len(result) > 0:
                for i in result:
                    bot.send_message(chat_id, f"ID Reminder: {i[2]}\nWaktu: {convert_utc_to_usertz(i[1], 'WIB')}\nAgenda: {i[0]}")
            else:
                bot.send_message(chat_id, "Anda belum memiliki agenda")

    def remove_agenda(self, msg):
        chat_id = msg.chat.id
        text = msg.text.split(' ')
        text = text[2:]
        if len(text) != 0:
            if text[0].isdigit():
                agenda = int(text[0])
                with create_conn() as conn:
                    cursor = conn.cursor()
                    query = "DELETE FROM reminder_user WHERE id_reminder = %s AND id_telegram = %s"
                    try:
                        cursor.execute(query, (agenda, chat_id))
                        bot.send_message(chat_id, "Agenda telah Dihapus")
                    except Error:
                        bot.send_message(chat_id, "Agenda tidak ditemukan")
            else:
                bot.send_message(chat_id, "WHY U ISI SELAIN ANGKA")
        else:
            bot.send_message(chat_id, "Format agenda tidak sesuai\n"
                                      "Silahkan mengikuti contoh dibawah ini\n"
                                      "/agenda hapus 123456")


list_pengu = ListPengumuman()
pengu = InsertPengumuman()
del_pengu = DeletePengumuman()
up_pengu = UpdatePengumuman()
daftar = DaftarUser()
helper = Help()
agenda = Agenda()

bot.register_message_handler(helper.help, commands=["help", "start", "bantuan"])
bot.register_message_handler(agenda.router, commands=["agenda"])
bot.register_message_handler(pengu.first_step, commands=["insert"])
bot.register_message_handler(daftar.get_nama, commands=["daftar"])
bot.register_message_handler(list_pengu.send_list, commands=["list"])
bot.register_message_handler(del_pengu.deletePengumuman, commands=["del"])
bot.register_message_handler(up_pengu.first_step, commands=["update"])

if __name__ == '__main__':
    get_prodi()
    get_jurusan()
    print("BOT IS BERLARI")
    bot.polling()
