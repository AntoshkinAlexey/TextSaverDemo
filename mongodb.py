"""
Модуль предназначен для определения функций, работающих с базой данных

"""
import datetime
import os
import random
import re
import string

import pytz

import admin
from const import mdb, bot
from text import file_is_large_for_storage


def get_user(user_id):
    """
    :param user_id: id пользователя
    :return: возвращается пользователь

    """
    user_id = str(user_id)
    try:
        for user in mdb.users.find({"user_id": user_id}):
            return user
    except Exception as err:
        admin.error(error_admin_text='Get пользователя из базы данных ' + str(err))
        return None


def insert_user(user_id):
    """
    :param user_id: id пользователя
    вставляется пользователь или
    обновляется информация о пользователе, если он уже присутствует в БД

    """
    user_id = str(user_id)

    fields = {
        'user_id': user_id,
        'texts': [],
        'format': 'pdf',
        'used_memory': 0,
        'max_memory': 2097152,
    }

    old_user = get_user(user_id)
    for field in fields:
        if old_user is not None and field in old_user:
            fields[field] = old_user[field]

    try:
        mdb.users.update_one({"user_id": user_id}, {'$set': fields}, upsert=True)
    except Exception as err:
        admin.error(error_admin_text='Add пользователя в базу данных ' + str(err))


def update_user(user_id, keys):
    """
    :param user_id: id пользователя
    :param keys: ключи, которые нужно обновить
    обновляется информация о пользователе

    """
    user_id = str(user_id)
    if keys == {}:
        return
    try:
        mdb.users.update_one({"user_id": user_id}, {'$set': keys}, upsert=True)
    except Exception as err:
        admin.error(error_admin_text='Update пользователя в базе данных ' + str(err))


def delete_user(user_id):
    """
    :param user_id: id пользователя
    удаляется пользователь

    """
    user_id = str(user_id)
    try:
        mdb.users.delete_many({"user_id": user_id})
    except Exception as err:
        admin.error(error_admin_text='Delete пользователя в базе данных ' + str(err))


def get_all_users(params):
    """
    :param params: аргументы поиска
    :return находятся все пользователи, удовлетворяющие параметрам params

    """
    try:
        return mdb.users.find(params)
    except Exception as err:
        admin.error(error_admin_text='Get All пользователей из базы данных ' + str(err))
        return None


def insert_session(chat_id, name, args):
    """
    :param chat_id: id чата
    :param name: название сессии
    :param args: аргументы
    Создаётся сессия с аргументами args и названием name

    """
    chat_id = str(chat_id)
    session = {
        "chat_id": chat_id,
        "name": name,
        "args": args
    }
    try:
        mdb.sessions.update_one({"chat_id": chat_id}, {'$set': session}, upsert=True)
    except Exception as err:
        admin.error(error_admin_text='Insert session ' + str(err))


def find_session(chat_id):
    """
    :param chat_id: id чата
    :return: сессия

    """
    try:
        chat_id = str(chat_id)
        for session in mdb.sessions.find({"chat_id": chat_id}):
            return session
    except Exception as err:
        admin.error(error_admin_text='Find session ' + str(err))
        return None


def erase_session(chat_id):
    """
    :param chat_id: id чата
    Удаляется сессия

    """
    try:
        chat_id = str(chat_id)
        mdb.sessions.delete_many({"chat_id": chat_id})
    except Exception as err:
        admin.error(error_admin_text='Delete session ' + str(err))


def get_text(text_code):
    """

    :param text_code: код текста
    :return: возвращается информация о тексте
    """
    try:
        text_code = str(text_code)
        for text in mdb.texts.find({"code": text_code}):
            return text
    except Exception as err:
        admin.error(error_admin_text='Get text ' + str(err))
        return None


def new_text_code():
    """

    :return: возвращается новый уникальный код для текста,
    который позже будет использоваться в ссылках
    """
    try:
        while True:
            letters_and_digits = string.ascii_letters + string.digits
            rand_string = ''.join(random.sample(letters_and_digits, 9))
            if get_text(rand_string) is None:
                return rand_string
    except Exception as err:
        admin.error(error_admin_text='New text code ' + str(err))
        return None


def insert_text(chat_id, text, lines_cnt):
    """
    :param lines_cnt: количество строк в пдф файле
    :param chat_id: id чата
    :param text: новый текст
    :return возвращается код созданного текста

    Создаётся новый текст

    """
    try:
        chat_id = str(chat_id)

        code = new_text_code()

        date = datetime.datetime.now(pytz.timezone('Europe/Moscow')) \
            .replace(microsecond=0, hour=0, minute=0, second=0) \
            .replace(tzinfo=None)
        date = re.split(' ', str(date), maxsplit=1)[0]
        year, month, day = re.split('-', date)
        date = day + '.' + month + '.' + year

        text_data = {
            'name': 'New Text',
            'date': date,
            'beautiful_date': admin.beautiful_date(date),
            'data': text,
            'code': code,
            'link': 'https://t.me/TextSaver_bot?start=' + str(code),
            'lines': lines_cnt,
            'chat_id': chat_id,
            'txt_file': None,
            'bytes': 0
        }

        file_name = str(code) + ".txt"
        file_obj = open(file_name, "w+")
        try:
            file_obj.write(text_data['data'])
            file_obj.close()
            text_data['bytes'] = os.stat(file_name).st_size
            file_obj = open(file_name, "rb")
            text_data['txt_file'] = file_obj.read()
        except Exception as err:
            admin.error(error_admin_text='Очень Важно! Не получилось создать txt файл в БД '
                                         + str(err))
        finally:
            file_obj.close()
            os.remove(file_name)

        user = get_user(chat_id)
        user['texts'].append(code)
        user['used_memory'] = user['used_memory'] + text_data['bytes']
        if user['max_memory'] >= user['used_memory']:
            update_user(user_id=chat_id, keys=user)
            mdb.texts.update_one({"code": code}, {'$set': text_data}, upsert=True)
            return code
        bot.send_message(chat_id, text=file_is_large_for_storage(), parse_mode='html')
        return None
    except Exception as err:
        admin.error(error_admin_text='Insert text ' + str(err))
        return None


def erase_text(text_code):
    """
    :param text_code: code текста
    Удаляется текст

    """
    try:
        text_code = str(text_code)
        text = get_text(text_code)
        if text is None:
            return
        mdb.texts.delete_many({"code": text_code})
        user = get_user(text['chat_id'])
        user['texts'].remove(text_code)
        user['used_memory'] -= text['bytes']
        update_user(user_id=text['chat_id'], keys=user)
    except Exception as err:
        admin.error(error_admin_text='Delete text ' + str(err))


def update_text(text_code, keys):
    """
    :param text_code: code текста
    :param keys: обновляемые ключи
    обновляет информацию о тексте

    """
    text_code = str(text_code)
    if keys == {}:
        return
    try:
        mdb.texts.update_one({"code": text_code}, {'$set': keys}, upsert=True)
    except Exception as err:
        admin.error(error_admin_text='Update text в базе данных ' + str(err))


def get_stats():
    """
    Собирает статистику по базе данных.
    :return: Статистика по базе данных.
    """
    stats = {
        'Number of files': 0,
        'Number of users': 0,
        'Number of users with 1 Text': 0,
        'Number of users with 5 Texts': 0,
        'Number of premium modes': 0,
        'Memory used in the database': '0MB/512MB',
    }
    try:
        stats['Memory used in the database'] = str((mdb.command("dbstats")['dataSize'] + mdb.command("dbstats")['indexSize']) // 1024 // 1024) + "MB/512MB"
    except Exception as err:
        admin.error(error_admin_text='Ошибка при получении занятой памяти в бд ' + str(err))

    try:
        for user in get_all_users({}):
            stats['Number of users'] += 1
            text_count = 0
            if 'texts' in user:
                text_count = len(user['texts'])
            stats['Number of files'] += text_count
            if text_count > 0:
                stats['Number of users with 1 Text'] += 1
            if text_count > 5:
                stats['Number of users with 5 Texts'] += 1
            if 'max_memory' in user and user['max_memory'] > 2 * 1024 * 1024:
                stats['Number of premium modes'] += 1
    except Exception as err:
        admin.error(error_admin_text='Ошибка при получении статистики ' + str(err))
        return None
    return stats



