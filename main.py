import os
from multiprocessing import Process
from signal import signal, SIGINT
from telebot import TeleBot
from dotenv import load_dotenv

load_dotenv()
telebot = TeleBot(os.environ['API'])

def start_bot():
    os.system('python app.py')


def start_reminder():
    os.system('python sender.py')


if __name__=='__main__':
    p1 = Process(target=start_reminder)
    p2 = Process(target=start_bot)
    p1.start()
    p2.start()
    p1.join()
    p2.join()