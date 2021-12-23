import os

from telebot import TeleBot, types
from dotenv import load_dotenv
from dataclasses import dataclass
from lib import checkuser, logfunc, create_conn, convert_to_utc, checksiswa
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

@dataclass
class User:
    id_tele = int
    jurusan = int
    prodi = int
    tingkat = int

    def getastuple(self):
        id_tele = self.id_tele
        jurusan = self.jurusan
        prodi = self.prodi
        tingkat = self.tingkat
        return (id_tele,jurusan,prodi,tingkat)

    def setfromtuple(self, datatuple : tuple):
        self.id_tele, self.jurusan, self.prodi, self.tingkat = datatuple

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
        chat_id = message.chat.id
        try:
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
        chat_id = message.chat.id
        try:
            prodi = int(message.text)
            if prodi not in dict_prodi:
                msg = bot.send_message(chat_id=chat_id, text="Silahkan isi sesuai id Prodi")
                bot.register_next_step_handler(msg, self.forth_step)
            else:
                data = global_dict[chat_id]
                data.prodi = prodi
                msg = bot.reply_to(message, 'Tingkat : ')
                bot.register_next_step_handler(msg, self.fifth_step)
        except Exception as e:
            logfunc("5TH Pengumuman", e)
            msg = bot.send_message(chat_id=chat_id, text="Silahkan isi sesuai input")
            bot.register_next_step_handler(msg, self.forth_step)

    def fifth_step(self, message):
        chat_id = message.chat.id
        try:
            tingkat = int(message.text)
            if tingkat not in [1,2,3,4]:
                bot.register_next_step_handler(
                    bot.send_message(chat_id=chat_id, text="Tingkat yang tersedia hanya 1 sampai 4")
                    , self.fifth_step)
            else:
                data = global_dict[chat_id]
                data.tingkat = tingkat
                msg = bot.send_message(chat_id, "Waktu dengan format (DD/MM/YYYY HH:MM) :")
                bot.register_next_step_handler(msg, self.six_step)
        except Exception as e:
            logfunc("FIFTH_STEP_DATE", e)
            msg = bot.send_message(chat_id=chat_id, text="Silahkan masukkan sesuai input")
            bot.register_next_step_handler(msg, self.fifth_step)


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
        except ValueError:
            msg = bot.reply_to(message, "Silahkan masukkan sesuai format (DD/MM/YYYY HH:MM)")
            bot.register_next_step_handler(msg, self.six_step)
        except Exception as e:
            logfunc('commit database', e)
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin terjadi error silahkan lapor ke admin')

    def commit_to_database(self,message):
        chat_id = message.chat.id
        keputusan = message.text
        try:
            user = global_dict[chat_id]
            if (keputusan == u'ya'):
                insert = "INSERT INTO isi_pengumuman VALUES (%s,%s,%s,%s,%s,%s,%s)"
                val = user.getastuple()
                with create_conn() as conn:
                    cursor = conn.cursor()
                    cursor.execute(insert, val)
                    conn.close()
                bot.send_message(chat_id, "ok data sudah terinput")
            else:
                msg = bot.send_message(chat_id, "Silahkan tekan -> /daftar untuk melakukan pendaftaran ulang")
                bot.register_next_step_handler(msg, self.first_step)
            # remove used object at user_dict
            del global_dict[chat_id]
        except Exception as e:
            del global_dict[chat_id]
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
        try:
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
            del global_dict[chat_id]
            logfunc("Del GetPengumuman", e)

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
            bot.reply_to(message, 'Silahkan ulangi kembali')


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
                if data is None:
                    bot.send_message(chat_id, "Pengumuman tidak ditemukan")
                else:
                    user.setfromtuple(data)
                    global_dict[chat_id] = user
                    bot.send_message(chat_id, f"Isi Pengumuman : {user.isi}")
                    msg = bot.reply_to(message, 'Isi yang mau diganti : ')
                    bot.register_next_step_handler(msg, self.third_step)
        except Exception as e:
            logfunc('nama', e)
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin')

    def third_step(self, message):
        chat_id = message.chat.id
        try:
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
            bot.register_next_step_handler(bot.send_message(chat_id, "Silahkan isi kembali"), self.first_step)

    def forth_step(self, message):
        chat_id = message.chat.id
        try:
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
                bot.send_message(chat_id, f"Tingkat : {data.tingkat}\nketik skip untuk melewati")
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
        chat_id = message.chat.id
        keputusan = message.text
        try:
            user = global_dict[chat_id]
            if (keputusan == u'ya'):
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
            del global_dict[chat_id]
            logfunc('commit database', e)
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin terjadi error silahkan lapor ke admin')

class DaftarUser:
    def first_step(self, msg):
        chat_id = msg.chat.id
        text = msg.text
        if not checksiswa(chat_id):
            bot.send_message(chat_id, "Anda sudah terdaftar")
        else:
            try:
                pesan = "\n".join(text_jurusan)
                bot.send_message(chat_id=chat_id, text=f"List jurusan: \n{pesan}")
                msg = bot.send_message(chat_id, "Silahkan masukkan jurusan anda anda")
                bot.register_next_step_handler(msg, self.second_step)
            except Exception as e:
                logfunc('first step Daftar', e)
                bot.send_message(chat_id, "Terjadi error silahkan ulang kembali")


    def second_step(self, msg):
        chat_id = msg.chat.id
        try:
            text = int(msg.text)
            user = User()
            user.id_tele = chat_id
            if text not in dict_jurusan:
                msg = bot.send_message(chat_id, "\n".join(text_jurusan)+
                                       "\nJurusan tidak ditemukan, silahkan masukkan jurusan anda kembali")
                bot.register_next_step_handler(msg, self.second_step)
            else:
                user.jurusan = text
                global_dict[chat_id] = user
                pesan = "\n".join(text_prodi)
                bot.send_message(chat_id, f"List Prodi :\n{pesan}")
                msg = bot.send_message(chat_id, "Silahkan masukkan prodi anda")
                bot.register_next_step_handler(msg, self.third_step)
        except ValueError:
            msg = bot.send_message(chat_id, "Input tidak sesuai, silahkan masukkan kembali")
            bot.register_next_step_handler(msg, self.second_step)
        except Exception as e:
            del global_dict[chat_id]
            logfunc('second step Daftar', e)
            bot.send_message(chat_id, "Terjadi error silahkan ulang kembali")

    def third_step(self, msg):
        chat_id = msg.chat.id
        try:
            text = int(msg.text)
            if text not in dict_prodi:
                msg = bot.send_message(chat_id, "\n".join(text_prodi)+"\nInput tidak sesuai, silahkan masukkan kembali")
                bot.register_next_step_handler(msg, self.third_step)
            else:
                user = global_dict[chat_id]
                user.prodi = text
                msg = bot.send_message(chat_id, "Silahkan masukkan tingkat anda")
                bot.register_next_step_handler(msg, self.fourth_step)
        except ValueError as val:
            del global_dict[chat_id]
            logfunc('third step Daftar', val)
            msg = bot.send_message(chat_id, "Input tidak sesuai, silahkan masukkan kembali")
            bot.register_next_step_handler(msg, self.third_step)
        except Exception as e:
            del global_dict[chat_id]
            logfunc('third step Daftar', e)
            bot.send_message(chat_id, "Terjadi error silahkan ulang kembali")

    def fourth_step(self, msg):
        chat_id = msg.chat.id
        try:
            text = int(msg.text)
            print(text)
            user = global_dict[chat_id]
            if text in range(1,4):
                user.tingkat = text
                data = user.getastuple()
                pesan = f"Tingkat : {data[3]}\nJurusan : {data[1]}\nProdi : {data[2]}\n"
                msg = bot.send_message(chat_id, pesan)
                bot.register_next_step_handler(msg, self.fifth_step)
            else:
                bot.send_message(chat_id, "Input tingkat hanya 1 sampai 4")
                msg = bot.send_message(chat_id, "Silahkan masukkan tingkat anda")
                bot.register_next_step_handler(msg, self.fourth_step)
        except ValueError as val:
            logfunc('fourth step Daftar', val)
            msg = bot.send_message(chat_id, "Input tidak sesuai, silahkan masukkan kembali")
            bot.register_next_step_handler(msg, self.fourth_step)
        except Exception as e:
            del global_dict[chat_id]
            logfunc('fourth step Daftar', e)
            bot.send_message(chat_id, "Terjadi error silahkan ulang kembali")



    def fifth_step(self, msg):
        chat_id = msg.chat.id
        try:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('ya', 'tidak')
            msg = bot.send_message(chat_id, "Apakah anda ingin menambahkan data? (ya/tidak)", reply_markup=markup)
            bot.register_next_step_handler(msg, self.commit_database_step)
        except Exception as e:
            del global_dict[chat_id]
            logfunc('commit database', e)
            bot.send_message(chat_id, "Terjadi error silahkan ulang kembali")

    def commit_database_step(self, msg):
        chat_id = msg.chat.id
        try:
            text = msg.text
            if text == 'ya':
                user = global_dict[chat_id]
                val = user.getastuple()
                insert = """
                INSERT INTO user (id_tele, nama, jurusan, prodi, tingkat)
                """
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
        
        *Bantuan (Admin Only)*
Untuk melihat daftar pengumuman silahkan ketik /list
Untuk menghapus pengumuman silahkan ketik /del
Untuk memasukkan pengumuman silahkan ketik /insert
Untuk mengupdat/mengubah pengumuman silahkan ketik /update
        
Note:
        Perhatikan keyword yang ditulis
        """
        bot.send_message(chat_id, pesan, parse_mode='Markdown')


list_pengu = ListPengumuman()
pengu = InsertPengumuman()
del_pengu = DeletePengumuman()
up_pengu = UpdatePengumuman()
daftar = DaftarUser()
helper = Help()

bot.register_message_handler(helper.help, commands=["help", "start", "bantuan"])
bot.register_message_handler(pengu.first_step, commands=["insert"])
bot.register_message_handler(daftar.first_step, commands=["daftar"])
bot.register_message_handler(list_pengu.send_list, commands=["list"])
bot.register_message_handler(del_pengu.deletePengumuman, commands=["del"])
bot.register_message_handler(up_pengu.first_step, commands=["update"])


if __name__=='__main__':
    get_prodi()
    get_jurusan()
    print("BOT IS BERLARI")
    bot.polling()

