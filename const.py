"""
Модуль содержит константы

"""

import telebot
import pymongo

TOKEN = "#TOKEN"
bot = telebot.TeleBot(TOKEN)
mdb = pymongo.MongoClient(
    "mongodb+srv://TextSaver:password@textsaver.m8aw4.mongodb.net/TextSaver?"
    "retryWrites=true&w=majority",
    ssl=True
)["TextSaver"]  # переменная для работы с монго

admins = ['374683082']
GROUP_ID = '-1001161732809'

PDF_LEN = 81
MAX_FILE_SIZE = 2 * 1024 * 1024
