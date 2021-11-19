import os

from telebot import TeleBot, types
from dotenv import load_dotenv
from dataclasses import dataclass
from lib import checkuser, create_cursor, logfunc

# Global Variable
load_dotenv()
TOKEN = os.getenv('API')
bot = TeleBot()

global_dict = {}

@dataclass
class DataPengumu:
    id_tele = int
    isi = str
    jurusan = int
    prodi = int
    tingkat = int

class Pengumuman:
    def first_step(self,message):
        chat_id = int(message.chat.id)
        try:
            if checkuser(chat_id):
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
        except:
            logfunc("5TH Pengumuman")

    def fifth_step(self, message):
        try:
            chat_id = message.chat.id
            tingkat = message.text
            data = global_dict[chat_id]
            data.tingkat = tingkat
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('ya', 'tidak')
            msg = bot.reply_to(message, f'Isi: {data.isi}\nJurusan : {data.jurusan}\nProdi : {data.prodi}\nTingkat : {data.tingkat}', reply_markup=markup)
            bot.register_next_step_handler(msg, self.commit_to_database)
        except:
            logfunc('commit database', e)
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin terjadi error silahkan lapor ke admin')

    def commit_to_database(self,message):
        try:
            chat_id = message.chat.id
            keputusan = message.text
            user = global_dict[chat_id]
            cursor = create_cursor()
            if (keputusan == u'ya'):
                insert = "INSERT INTO user (tele_id,nama,alamat) VALUES (%s,%s,%s)"
                val = (user.teleg_id, user.nama, user.alamat)
                try:
                    with create_cursor() as conn:
                        conn.execute(insert, val)
                    bot.send_message(chat_id, "ok data sudah terinput")
                except Exception as e:
                    bot.send_message(chat_id, "terjadi error silahkan ulang kembali")
                    logfunc('commit database', e)
            else:
                bot.send_message(chat_id, "Silahkan tekan -> /daftar untuk melakukan pendaftaran ulang")
            # remove used object at user_dict
            del global_dict[chat_id]
            cursor.close()
        except Exception as e:
            logfunc('commit database', e)
            bot.reply_to(message, 'oooops terjadi error silahkan lapor ke admin terjadi error silahkan lapor ke admin')