import os
from multiprocessing import Process
from telebot import TeleBot
from dotenv import load_dotenv

load_dotenv()
telebot = TeleBot(os.environ['API'])

def start_bot():
    os.system('python app.py')

def start_reminder_pengumuman():
    os.system('python rempeng.py')

def start_reminder_user():
    os.system('python rempeng.py')

if __name__=='__main__':
    p1 = Process(target=start_reminder_pengumuman)
    p2 = Process(target=start_bot)
    p3 = Process(target=start_reminder_user)
    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()