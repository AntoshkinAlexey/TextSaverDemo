"""
Модуль main, обрабатывает поступившие сообщения от пользователя

"""

import re
from telebot import types

import admin
import const
import mongodb as backend
import text
import keyboard
import callback

bot = const.bot


# for i in range(70):
#     backend.insert_text('374683082', text='Some Text', lines_cnt=11)

@bot.message_handler(commands=["start", "help"])
def start_chat(text_data):
    """
    :param message: информация о сообщении
    :return: ничего не возвращается

    """
    if text_data.chat.type == "private":
        try:
            chat_id = str(text_data.chat.id)
            message = text_data.text
            admin.log(chat_id=chat_id,
                      username=text_data.from_user.username,
                      first_name=text_data.from_user.first_name,
                      last_name=text_data.from_user.last_name,
                      text=message)
            user = backend.get_user(chat_id)
            backend.insert_user(chat_id)  # запоминаем пользователя в бд
            if user is None:
                bot.send_message(chat_id=chat_id,
                                 text=text.greeting(),
                                 parse_mode='html',
                                 reply_markup=keyboard.menu_static(chat_id))
            admin.check_session(text_data, True)
            if message == '/start':
                bot.send_message(chat_id=chat_id,
                                 text=text.greeting(),
                                 parse_mode='html',
                                 reply_markup=keyboard.menu_static(chat_id))
                bot.send_message(chat_id=chat_id,
                                 text=text.menu(),
                                 reply_markup=keyboard.menu(),
                                 parse_mode='html')
            elif message == '/help':
                bot.send_message(chat_id=chat_id,
                                 text=text.help(),
                                 parse_mode='MarkdownV2',
                                 reply_markup=keyboard.menu_static(chat_id))
            elif re.match('/start ', message):
                text_code = re.split(' ', message)[1]
                user_text = backend.get_text(text_code)
                if user_text is None:
                    bot.send_message(chat_id=chat_id,
                                     text=text.text_deleted(),
                                     parse_mode='html')

                if str(user_text['chat_id']) == chat_id:
                    admin.send_document(chat_id, text_code, user_text)
                else:
                    admin.send_document(chat_id, text_code, user_text=user_text, is_shared=True)

        except Exception as err:
            admin.error(error_admin_text='Первое сообщение от пользователя '
                                         + str(err))


@bot.message_handler(content_types=["text"])
def continue_chat(text_data):
    """
    :param text_data: информация о сообщении
    :return: ничего не возвращается

    """
    try:
        if text_data.chat.type == "private":
            chat_id = str(text_data.from_user.id)
            message = text_data.text
            admin.log(chat_id=chat_id,
                      username=text_data.from_user.username,
                      first_name=text_data.from_user.first_name,
                      last_name=text_data.from_user.last_name,
                      text=message)
            backend.insert_user(chat_id)  # запоминаем пользователя в бд
            if message == 'TextSaver':
                admin.check_session(text_data, True)
                bot.send_message(chat_id=chat_id,
                                 text=text.menu(),
                                 reply_markup=keyboard.menu(),
                                 parse_mode='html')
            elif message == 'Stats 📊':
                admin.check_session(text_data, True)
                bot.send_message(chat_id=chat_id,
                                 text=text.stats(),
                                 parse_mode='html')
            elif message == 'Premium 💲':
                admin.check_session(text_data, True)
                if backend.get_user(chat_id)['max_memory'] > 2 * 1024 * 1024:
                    bot.send_message(chat_id=chat_id, text="You already have premium mode.")
                else:
                    bot.send_invoice(chat_id=chat_id,
                                     title="Premium payment",
                                     invoice_payload="Счёт",
                                     description=text.payment(),
                                     provider_token="381764678:TEST:56596",
                                     currency="RUB",
                                     prices=[types.LabeledPrice(label="RUB", amount=50000)])
            elif message == '/settings':
                admin.check_session(text_data, True)
                bot.send_message(chat_id=chat_id,
                                 text=text.settings(),
                                 reply_markup=keyboard.settings(chat_id),
                                 parse_mode='html')
            admin.check_session(text_data)
    except Exception as err:
        admin.error(error_admin_text='Обработка сообщения от пользователя '
                                     + str(err))


@bot.callback_query_handler(func=lambda text_data: True)
def callback_text(text_data):
    """
    :param text_data: информация о сообщении
    :return: ничего не возвращается

    """

    try:
        chat_id = str(text_data.from_user.id)
        backend.insert_user(chat_id)  # запоминаем пользователя в бд
        message = text_data.data
        admin.log(chat_id=chat_id,
                  username=text_data.from_user.username,
                  first_name=text_data.from_user.first_name,
                  last_name=text_data.from_user.last_name,
                  text=message)
        admin.check_session(text_data, True)
        if re.match('menu', message):
            callback.inline_menu(text_data)
        elif re.match('settings', message):
            callback.inline_settings(text_data)


    except Exception as err:
        admin.error(error_admin_text='Обработка callback от пользователя '
                                     + str(err))


@bot.message_handler(content_types=['document'])
def file_handler(text_data):
    """
    :param text_data: информация о сообщении
    Принимает файлы

    """
    admin.check_session(text_data)


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    """
    :param pre_checkout_query: информация о платеже
    Подтверждает оплату.
    """
    try:
        if backend.get_user(pre_checkout_query.from_user.id)['max_memory'] > 2 * 1024 * 1024:
            bot.send_message(chat_id=pre_checkout_query.from_user.id, text="You already have premium mode.")
            bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False,
                                          error_message="Something went wrong. Try again in a "
                                                        "few minutes.")
        else:
            bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True, error_message="Something went wrong. Try again in a "
                                                                                        "few minutes.")
    except Exception as err:
        admin.error(error_admin_text='Ошибка при подтверждении оплаты premium ' + str(err))


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    try:
        backend.update_user(message.chat.id, {'max_memory': 10 * 1024 * 1024})
    except Exception as err:
        admin.error(error_admin_text='Ошибка при оплате подписки '
                                     + str(err), error_user_text="Something went wrong. Wait a bit, support is "
                                                                 "already solving your issue.")
    bot.send_message(message.chat.id, 'Thanks for payment! Now You have access to extended storage.')


bot.polling(none_stop=True)
