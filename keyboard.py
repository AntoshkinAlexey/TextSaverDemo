"""
Модуль для создания клавиатур

"""

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, KeyboardButton
import admin
import mongodb as backend


def menu_static(chat_id):
    """
    :param chat_id: id чата
    :return: Клавиатура с главной кнопкой

    """
    try:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        main_button = KeyboardButton(text="TextSaver")
        premium_button = KeyboardButton(text="Premium 💲")
        keyboard.add(main_button, premium_button)
        if admin.is_admin(chat_id):
            stats_button = KeyboardButton(text="Stats 📊")
            keyboard.add(stats_button)
        return keyboard
    except Exception as err:
        admin.error(error_admin_text='menu_static keyboard ' + str(err))
        return None


def menu():
    """
    :return Возвращает меню inline

    """
    keyboard = InlineKeyboardMarkup()
    create_text = InlineKeyboardButton(text="Create New Text 📝",
                                       callback_data="menu_create_text")
    my_texts_but = InlineKeyboardButton(text="My Texts 📁",
                                    callback_data="menu_my_texts")
    keyboard.add(create_text)
    keyboard.add(my_texts_but)
    return keyboard


def next(prefix):
    """
    :return: Возвращает кнопку next

    """
    keyboard = InlineKeyboardMarkup()
    next_button = InlineKeyboardButton(text="Next ➡️",
                                       callback_data=str(prefix) + "_next")
    keyboard.add(next_button)
    return keyboard


def text_info(text_code):
    """
    :param text_code: код текста
    :return: Возвращается кнопки редактирования текста

    """
    try:
        keyboard = InlineKeyboardMarkup()
        delete = InlineKeyboardButton(text="Delete ❌️",
                                      callback_data="menu_delete_" + str(text_code))
        title = InlineKeyboardButton(text="Title 🏷",
                                     callback_data="menu_title_" + str(text_code))
        txt = InlineKeyboardButton(text=".txt",
                                   callback_data="menu_send_file_" + str(text_code) + "_txt")
        pdf = InlineKeyboardButton(text=".pdf",
                                   callback_data="menu_send_file_" + str(text_code) + "_pdf")
        tg_mes = InlineKeyboardButton(text=".tg",
                                      callback_data="menu_send_file_" + str(text_code) + "_mes")
        edit = InlineKeyboardButton(text="Edit 📝",
                                    callback_data="menu_edit_" + str(text_code))

        back_button = InlineKeyboardButton(text='Back ⬅️',
                                           callback_data='menu_my_texts_back')
        keyboard.add(back_button)
        keyboard.add(title, edit)
        keyboard.add(txt, pdf, tg_mes)
        keyboard.add(delete)
        return keyboard
    except Exception as err:
        admin.error(error_admin_text='Не получилось создать клавиатуру ' + str(err))
        return None


def shared_text_info(text_code):
    """
    :param text_code: код текста
    :return: Возвращается кнопки редактирования текста, которым кто-то поделился

    """
    try:
        keyboard = InlineKeyboardMarkup()
        save = InlineKeyboardButton(text="Save ✅",
                                    callback_data="menu_save_" + str(text_code))
        update = InlineKeyboardButton(text="Update 🔄",
                                      callback_data="menu_update_" + str(text_code))
        txt = InlineKeyboardButton(text=".txt",
                                   callback_data="menu_send_file_" + str(text_code) + "_txt")
        pdf = InlineKeyboardButton(text=".pdf",
                                   callback_data="menu_send_file_" + str(text_code) + "_pdf")
        tg_mes = InlineKeyboardButton(text=".tg",
                                      callback_data="menu_send_file_" + str(text_code) + "_mes")

        back_button = InlineKeyboardButton(text='Back ⬅️',
                                           callback_data='menu_my_texts_back')
        keyboard.add(back_button)
        keyboard.add(txt, pdf, tg_mes)
        keyboard.add(update, save)
        return keyboard
    except Exception as err:
        admin.error(error_admin_text='Не получилось создать клавиатуру ' + str(err))
        return None


def my_texts(chat_id, first=0, user=None):
    """
    :param user: информация о пользователе
    :param chat_id: id чата
    :return: клавиатура с текстами

    """
    try:
        keyboard = InlineKeyboardMarkup(row_width=5)
        if user is None:
            user = backend.get_user(chat_id)
        back_button = InlineKeyboardButton(text='Back to Menu ⬅️',
                                           callback_data='menu_back')
        keyboard.add(back_button)
        column = [[], [], [], [], []]
        if len(user['texts']) == 0:
            return keyboard
        for i in range(first, min(len(user['texts']), first + 15)):
            but = InlineKeyboardButton(text=str(int(i + 1)),
                                       callback_data='menu_file_' + str(user['texts'][i]))
            column[i % 5].append(but)

        empty_button = InlineKeyboardButton(text=' ',
                                            callback_data='None')
        # while len(column[0]) < len(column[1]):
        #     column[0].append(empty_button)
        # while len(column[2]) < len(column[1]):
        #     column[2].append(empty_button)
        for i in range(len(column[0])):
            line = []
            for j in range(5):
                if i < len(column[j]):
                    line.append(column[j][i])
                else:
                    line.append(empty_button)
            keyboard.add(line[0], line[1], line[2], line[3], line[4])

        prev_button = InlineKeyboardButton(text='⬅️ Prev Page',
                                           callback_data='menu_my_texts_prevpage_'
                                                         + str(chat_id) + '_'
                                                         + str(first))
        next_button = InlineKeyboardButton(text='Next Page ➡️️',
                                           callback_data='menu_my_texts_nextpage_'
                                                         + str(chat_id) + '_'
                                                         + str(first))

        if first > 0 and first + 15 < len(user['texts']):
            keyboard.add(prev_button, next_button)
        elif first > 0:
            keyboard.add(prev_button)
        elif first + 15 < len(user['texts']):
            keyboard.add(next_button)

        return keyboard
    except Exception as err:
        admin.error(error_admin_text='Создание клавиатуры my_texts ' + str(err))
        return None


def yes_no(callback_text):
    """
    :param prefix: префикс для callback
    :return: клавиатура yes_no

    """
    keyboard = InlineKeyboardMarkup()
    yes_button = InlineKeyboardButton(text='Yes️',
                                      callback_data=callback_text + '_yes')
    no_button = InlineKeyboardButton(text='No',
                                     callback_data=callback_text + '_no')
    keyboard.add(no_button, yes_button)
    return keyboard


def settings(chat_id):
    """
    :param chat_id: id чата
    :return: клавиатура с настройками

    """
    try:
        chat_id = str(chat_id)
        user = backend.get_user(chat_id)

        def what_format(format_type):
            if user['format'] == format_type:
                return ' 🟢'
            return ' 🔴'

        keyboard = InlineKeyboardMarkup()
        pdf_button = InlineKeyboardButton(text='.pdf' + what_format('pdf'),
                                          callback_data='settings_format_pdf')
        txt_button = InlineKeyboardButton(text='.txt' + what_format('txt'),
                                          callback_data='settings_format_txt')
        keyboard.add(pdf_button, txt_button)
        return keyboard
    except Exception as err:
        admin.error(error_admin_text='Создание клавиатуры settings ' + str(err))
        return None
