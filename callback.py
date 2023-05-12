"""
Модуль для обработки нажатий на кнопки

"""

import re

import const
import admin
import text
import keyboard
import mongodb as backend

bot = const.bot


def inline_menu(text_data):
    """
    :param text_data: информация о callback
    Обрабатываются нажатия на кнопки InlineMenu

    """
    chat_id = str(text_data.from_user.id)
    message = re.split('menu_', text_data.data, maxsplit=1)[1]

    if re.match('create_text', message):
        try:
            message_id = None
            try:
                message_id = bot.edit_message_text(chat_id=chat_id,
                                                   message_id=text_data.message.message_id,
                                                   text=text.send_code(),
                                                   parse_mode='html').message_id
            except Exception:
                pass
            backend.insert_session(chat_id=chat_id,
                                   name='new_text',
                                   args={
                                       'delete_id': message_id
                                   })
        except Exception as err:
            admin.error('Create new text callback ' + str(err))
    elif re.match('my_texts', message):
        try:
            if re.match('my_texts_back', message):
                try:
                    bot.delete_message(chat_id=chat_id,
                                       message_id=text_data.message.message_id)
                except Exception:
                    pass
                message_id = bot.send_message(chat_id=chat_id,
                                              text=text.wait(),
                                              parse_mode='html').message_id
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=text.my_texts(chat_id),
                                      reply_markup=keyboard.my_texts(chat_id),
                                      parse_mode='html')
                return
            try:
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=text_data.message.message_id,
                                      text=text.wait(),
                                      parse_mode='html')
                if re.match('my_texts_prevpage', message):
                    message = re.split('my_texts_prevpage_', message)[1]
                    text_code, first = re.split('_', message)
                    first = int(first)
                    first -= 15
                    user = backend.get_user(chat_id)
                    while first >= len(user['texts']):
                        first -= 15
                    first = max(0, first)
                    bot.edit_message_text(chat_id=chat_id,
                                          message_id=text_data.message.message_id,
                                          text=text.my_texts(chat_id, first, user=user),
                                          reply_markup=keyboard.my_texts(chat_id, first, user=user),
                                          parse_mode='html')
                elif re.match('my_texts_nextpage', message):
                    message = re.split('my_texts_nextpage_', message)[1]
                    text_code, first = re.split('_', message)
                    first = int(first)
                    first += 15
                    user = backend.get_user(chat_id)
                    while first >= len(user['texts']):
                        first -= 15
                    first = max(0, first)
                    bot.edit_message_text(chat_id=chat_id,
                                          message_id=text_data.message.message_id,
                                          text=text.my_texts(chat_id=chat_id, first=first),
                                          reply_markup=keyboard.my_texts(chat_id=chat_id,
                                                                         first=first,
                                                                         user=user),
                                          parse_mode='html')
                else:
                    bot.edit_message_text(chat_id=chat_id,
                                          message_id=text_data.message.message_id,
                                          text=text.my_texts(chat_id),
                                          reply_markup=keyboard.my_texts(chat_id),
                                          parse_mode='html')
            except Exception:
                pass

        except Exception as err:
            admin.error('My texts callback ' + str(err))
    elif re.match('back', message):
        try:
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=text_data.message.message_id,
                                  text=text.menu(),
                                  reply_markup=keyboard.menu(),
                                  parse_mode='html')
        except Exception:
            pass
    elif re.match('file_', message):
        try:
            code = re.split('_', message)[1]
            try:
                bot.delete_message(chat_id=chat_id,
                                   message_id=text_data.message.message_id)
            except Exception:
                pass
            admin.send_document(chat_id, code)
        except Exception as err:
            admin.error('File callback ' + str(err))
    elif re.match('delete_', message):
        try:
            code = str(re.split('_', message)[1])
            if re.match('delete_yes_no_', message):
                message = re.split('delete_yes_no_', message)[1]
                code, confirm = re.split('_', message)
                try:
                    if confirm == 'yes':
                        backend.erase_text(code)
                        try:
                            bot.edit_message_text(chat_id=chat_id,
                                                  message_id=text_data.message.message_id,
                                                  text=text.wait(),
                                                  parse_mode='html')
                            bot.edit_message_text(chat_id=chat_id,
                                                  message_id=text_data.message.message_id,
                                                  text=text.my_texts(chat_id),
                                                  reply_markup=keyboard.my_texts(chat_id),
                                                  parse_mode='html')
                        except Exception:
                            pass
                    else:
                        try:
                            bot.delete_message(chat_id=chat_id,
                                               message_id=text_data.message.message_id)
                        except Exception:
                            pass
                        admin.send_document(chat_id, code)
                except Exception:
                    pass
            else:
                try:
                    bot.delete_message(chat_id=chat_id,
                                       message_id=text_data.message.message_id)
                except Exception:
                    pass
                bot.send_message(chat_id=chat_id,
                                 text=text.confirmation_text_deletion(),
                                 reply_markup=keyboard.yes_no('menu_delete_yes_no_' + code),
                                 parse_mode='html')
        except Exception as err:
            admin.error('Delete text callback ' + str(err))
    elif re.match('title_', message):
        try:
            code = re.split('_', message)[1]
            message_id = bot.send_message(chat_id=chat_id,
                                          text=text.change_title(),
                                          parse_mode='html').message_id
            backend.insert_session(chat_id=chat_id,
                                   name='change_title',
                                   args={
                                       'text_code': code,
                                       'delete_id': [message_id, text_data.message.message_id]
                                   })

        except Exception as err:
            admin.error('Change title callback ' + str(err))
    elif re.match('send_file_', message):
        try:
            message = re.split('send_file_', message)[1]
            code, out_format = re.split('_', message)
            user_text = backend.get_text(code)
            if user_text is None:
                bot.send_message(chat_id=chat_id,
                                 text=text.text_deleted(),
                                 parse_mode='html')
                return
            if out_format in ('txt', 'pdf'):
                try:
                    data = admin.create_document(code, out_format)
                    if data:
                        bot.send_document(chat_id=chat_id,
                                          document=data)
                    else:
                        bot.send_message(chat_id=chat_id,
                                         text=text.cant_output_text())
                except Exception as err:
                    admin.error(error_admin_text='Вывод файла в определённом формате ' + str(err))
            elif out_format == 'mes':
                try:
                    mes = user_text['data']
                    for pos in range(0, len(mes), 4096):
                        bot.send_message(chat_id=chat_id,
                                         text=str(mes[pos: pos + 4096]))
                except Exception:
                    bot.send_message(chat_id=chat_id,
                                     text=text.cant_output_text())
        except Exception as err:
            admin.error('File callback ' + str(err))
    elif re.match('edit_', message):
        try:
            code = re.split('_', message)[1]
            message_id = bot.send_message(chat_id=chat_id,
                                          text=text.send_code(),
                                          parse_mode='html').message_id
            backend.insert_session(chat_id=chat_id,
                                   name='edit_text',
                                   args={
                                       'text_code': code,
                                       'delete_id': [message_id, text_data.message.message_id]
                                   })
        except Exception as err:
            admin.error('Edit Text callback ' + str(err))
    elif re.match('save_', message):
        try:
            text_code = re.split('_', message)[1]
            user_text = backend.get_text(text_code)
            if user_text is None:
                bot.send_message(chat_id=chat_id,
                                 text=text.text_deleted(),
                                 parse_mode='html')
                return
            text_code = backend.insert_text(chat_id=chat_id,
                                            text=user_text['data'],
                                            lines_cnt=user_text['lines'])
            if text_code is None:
                return
            result = admin.send_document(chat_id, text_code)
            if result:
                try:
                    bot.delete_message(chat_id=chat_id,
                                       message_id=text_data.message.message_id)
                except Exception:
                    pass
        except Exception as err:
            admin.error('Save Text callback ' + str(err))
    elif re.match('update_', message):
        try:
            text_code = re.split('_', message)[1]
            result = admin.send_document(chat_id, text_code, is_shared=True)
            if result:
                try:
                    bot.delete_message(chat_id=chat_id,
                                       message_id=text_data.message.message_id)
                except Exception:
                    pass
        except Exception as err:
            admin.error('Update Text callback ' + str(err))


def inline_settings(text_data):
    """
    :param text_data: информация о callback
    Обрабатываются нажатия на кнопки Settings

    """
    chat_id = str(text_data.from_user.id)
    message = re.split('settings_', text_data.data, maxsplit=1)[1]

    if re.match('format_', message):
        message = re.split('format_', text_data.data, maxsplit=1)[1]
        if message == 'pdf':
            backend.update_user(chat_id, {'format': 'pdf'})
        else:
            backend.update_user(chat_id, {'format': 'txt'})

        try:
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=text_data.message.message_id,
                                  text=text.settings(),
                                  reply_markup=keyboard.settings(chat_id),
                                  parse_mode='html')
        except Exception:
            pass
