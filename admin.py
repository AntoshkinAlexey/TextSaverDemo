"""
Модуль обрабатывает логи и ошибки, а также некоторые администраторские функции

"""

import io
import math
import os
import re

from fpdf import FPDF

import const
import mongodb as backend
import keyboard
import text

bot = const.bot


def error(error_admin_text=None, user_id=None, error_user_text=None):
    """
    :param error_admin_text: текст с ошибкой для админа
    :param user_id: id пользователя
    :param error_user_text: текст про ошибку для пользователя

    """
    try:
        if error_admin_text is not None:
            message = '❗Произошла ошибка\n' + error_admin_text
            print(message)
            bot.send_message(const.GROUP_ID, message)
        if user_id is not None:
            bot.send_message(user_id, error_user_text)
    except Exception as err:
        print(err)
        pass


def log(chat_id, username, first_name, last_name, text):
    """
    :param chat_id: id чата
    :param username: username пользователя
    :param first_name: имя пользователя
    :param last_name: фамилия пользователя
    :param text: текст лога

    """
    try:
        message = str(chat_id) + ' ' + str(username) + ' ' + str(first_name) \
                  + ' ' + str(last_name) + ': ' + str(text)
        print(message)
        bot.send_message(const.GROUP_ID, message)
    except Exception as err:
        print(err)
        pass


def is_admin(chat_id):
    """
    :param chat_id: id чата
    :return: bool, админ или нет

    """
    return str(chat_id) in const.admins


def send_document(chat_id, code, user_text=None, is_shared=False):
    """
    :param is_shared: наш ли это файл
    :param user_text: если есть текст, то не надо его подгружать из БД
    :param chat_id: id чата
    :param code: код текста
    Отправляет информацию о тексте пользователю

    """
    if code is None or backend.get_text(code) is None:
        bot.send_message(chat_id=chat_id,
                         text=text.text_deleted(),
                         parse_mode='html')
        return False
    chat_id = str(chat_id)
    code = str(code)
    data = create_document(code, user_text=user_text, chat_id=chat_id)
    if not is_shared:
        try:
            assert data
            bot.send_document(chat_id=chat_id,
                              document=data,
                              caption=text.text_info(code, user_text=user_text),
                              reply_markup=keyboard.text_info(code),
                              parse_mode='Markdown')
        except Exception:
            bot.send_message(chat_id=chat_id,
                             text=text.text_info(code),
                             reply_markup=keyboard.text_info(code),
                             parse_mode='Markdown')
    else:
        try:
            assert data
            bot.send_document(chat_id=chat_id,
                              document=data,
                              caption=text.text_info(code,
                                                     user_text=user_text) + text.warning_delete(),
                              reply_markup=keyboard.shared_text_info(code),
                              parse_mode='Markdown')
        except Exception:
            bot.send_message(chat_id=chat_id,
                             text=text.text_info(code,
                                                 user_text=user_text) + text.warning_delete(),
                             reply_markup=keyboard.shared_text_info(code),
                             parse_mode='Markdown')
    return True


def beautiful_date(date):
    """
    :param date: дата
    :return: возвращает дату в красивом формате

    """
    month = [
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'June',
        'Jul',
        'Aug',
        'Sept',
        'Oct',
        'Nov',
        'Dec'
    ]
    date = re.split('[.]', date)
    return date[0] + ' ' + month[int(date[1]) - 1] + ' ' + date[2]


def create_document(code, type=None, user_text=None, chat_id=None):
    """
    :param code: код текста
    :param type: тип файла, если None, то пробуем pdf, в случае ошибки txt.
    :return: вовзращает созданный файл
    Функция создаёт pdf или txt файл

    """
    if user_text is None:
        user_text = backend.get_text(code)
    user = None
    if chat_id is not None:
        user = backend.get_user(chat_id)

    def pdf_file():
        """
        :return: pdf file

        """
        try:
            pdf = FPDF(format=(218, max(user_text['lines'] * 7, 297)))
            pdf.add_page()
            pdf.set_auto_page_break(True, 1)
            pdf.set_margins(1, 1, 1)
            pdf.add_font('DejaVu', '', 'font/ttf/DejaVuSansCondensed.ttf', uni=True)
            pdf.set_font("DejaVu", size=12)
            pdf.multi_cell(200, 7, txt=user_text['data'], align='L')
            pdf.close()
            file_obj = pdf.output('', 'S').encode('latin-1')
            file_obj = io.BytesIO(file_obj)
            file_obj.name = str(user_text['name']) + ".pdf"
            return file_obj
        except Exception as err:
            error(error_admin_text='Не получилось создать pdf file!!!' + str(err))
            return None

    def txt_file():
        """
        :return: txt file

        """
        try:
            assert user_text['txt_file']
            file_obj = io.BytesIO(user_text['txt_file'])
            file_obj.name = str(user_text['name']) + ".txt"
            return file_obj
        except Exception as err:
            error(error_admin_text='Не получилось создать txt file!!!' + str(err))
            return None

    file = None
    if type is None:
        if user and user['format'] == 'txt':
            file = txt_file()
        if file is None:
            file = pdf_file()
        if file is None:
            file = txt_file()
    elif type == 'txt':
        file = txt_file()
    elif type == 'pdf':
        file = pdf_file()
    return file


def check_session(text_data, delete=False):
    """
    :param text_data: информация о сообщении
    :param delete: нужно ли удалить сессию

    проверка сессий

    """
    try:
        chat_id = str(text_data.from_user.id)

        def get_txt_file(text_code, size=False):
            try:
                user_text = backend.get_text(text_code)

                file_name = str(user_text['code']) + ".txt"
                file_obj = open(file_name, "w+")
                data_size = None
                txt_file = None
                try:
                    file_obj.write(user_text['data'])
                    file_obj.close()
                    data_size = os.stat(file_name).st_size
                    file_obj = open(file_name, "rb")
                    txt_file = file_obj.read()
                except Exception as err:
                    error(error_admin_text='Очень Важно! '
                                           'Не получилось создать txt файл в check session '
                                           + str(err))
                finally:
                    file_obj.close()
                    os.remove(file_name)
                if size:
                    return txt_file, data_size
                else:
                    return txt_file
            except Exception as err:
                error(error_admin_text='Insert text ' + str(err))
                return None

        def check_edit(text_code, user_text, cnt_of_lines):
            if text_code is not None:
                old_text = backend.get_text(text_code)
                if old_text is None:
                    return None
                user = backend.get_user(chat_id)
                backend.update_text(text_code, {'data': user_text, 'lines': cnt_of_lines})
                txt_file, data_size = get_txt_file(text_code, size=True)
                new_memory = user['used_memory'] + data_size - old_text['bytes']

                if user['max_memory'] < new_memory:
                    backend.update_text(text_code, old_text)
                    bot.send_message(chat_id=chat_id,
                                     text=text.file_is_large_for_storage(),
                                     parse_mode='html')
                    return text_code
                backend.update_user(chat_id, {'used_memory': new_memory})
                backend.update_text(text_code, {'txt_file': txt_file, 'bytes': int(data_size)})
            else:
                text_code = backend.insert_text(chat_id=chat_id,
                                                text=user_text,
                                                lines_cnt=cnt_of_lines)
            return text_code

        def get_file(text_code=None):
            try:
                try:
                    bot.delete_message(chat_id=chat_id,
                                       message_id=text_data.message_id)
                except Exception:
                    pass

                file_info = bot.get_file(text_data.document.file_id)
                if file_info.file_size > const.MAX_FILE_SIZE:
                    bot.send_message(chat_id, text.file_is_large())
                    return text_code
                downloaded_file = bot.download_file(file_info.file_path)
                file = io.BytesIO(downloaded_file)
                data = file.readlines()
                user_text = ''
                cnt_of_lines = 10
                for line in data:
                    d_line = line.decode('utf-8')
                    cnt_of_lines += math.ceil(len(d_line) / const.PDF_LEN)
                    user_text += d_line
                return check_edit(text_code, user_text, cnt_of_lines)
            except Exception as err:
                error(error_admin_text='get_file' + str(err))
                bot.send_message(chat_id=chat_id,
                                 text=text.cant_parse_text(),
                                 parse_mode='html')
                return None

        def get_message(text_code=None):
            try:
                try:
                    bot.delete_message(chat_id=chat_id,
                                       message_id=text_data.message_id)
                except Exception:
                    pass
                user_text = text_data.text
                data = user_text.splitlines()
                cnt_of_lines = 10
                for line in data:
                    cnt_of_lines += math.ceil(len(line) / const.PDF_LEN)
                return check_edit(text_code, user_text, cnt_of_lines)
            except Exception as err:
                error(error_admin_text='get_message' + str(err))
                return None

        session = backend.find_session(chat_id)
        backend.erase_session(chat_id)
        is_cancel = 'text' in dir(text_data) and text_data.text == '/cancel'
        if session is None:
            return
        elif session['name'] == 'new_text':
            if delete or is_cancel:
                if is_cancel:
                    try:
                        bot.delete_message(chat_id=chat_id,
                                           message_id=text_data.message_id)
                    except Exception:
                        pass
                try:
                    bot.edit_message_text(chat_id=chat_id,
                                          message_id=session['args']['delete_id'],
                                          text=text.menu(),
                                          reply_markup=keyboard.menu(),
                                          parse_mode='html')
                except Exception:
                    pass
                finally:
                    return
            try:
                if text_data.content_type == 'document':
                    code = get_file()
                else:
                    code = get_message()

                try:
                    bot.delete_message(chat_id=chat_id,
                                       message_id=session['args']['delete_id'])
                except Exception:
                    pass
                if code is None:
                    bot.send_message(chat_id=chat_id,
                                     text=text.menu(),
                                     reply_markup=keyboard.menu(),
                                     parse_mode='html')
                else:
                    send_document(chat_id, code)
            except Exception:
                pass

        elif session['name'] == 'change_title':
            if delete or is_cancel:
                if is_cancel:
                    try:
                        bot.delete_message(chat_id=chat_id,
                                           message_id=text_data.message_id)
                    except Exception:
                        pass
                try:
                    bot.delete_message(chat_id=chat_id,
                                       message_id=session['args']['delete_id'][0])
                except Exception:
                    pass
                finally:
                    return
            code = session['args']['text_code']
            message = text_data.text
            if backend.get_text(code) is not None:
                if len(message) <= 30:
                    backend.update_text(code, {'name': message})
                else:
                    bot.send_message(chat_id=chat_id,
                                     text=text.title_is_large(),
                                     parse_mode='html')
            try:
                bot.delete_message(chat_id=chat_id,
                                   message_id=text_data.message_id)
            except Exception:
                pass
            for delete_id in session['args']['delete_id']:
                try:
                    bot.delete_message(chat_id=chat_id,
                                       message_id=delete_id)
                except Exception:
                    pass
            send_document(chat_id, code)
        elif session['name'] == 'edit_text':
            if delete or is_cancel:
                if is_cancel:
                    try:
                        bot.delete_message(chat_id=chat_id,
                                           message_id=text_data.message_id)
                    except Exception:
                        pass
                try:
                    bot.delete_message(chat_id=chat_id,
                                       message_id=session['args']['delete_id'][0])
                except Exception:
                    pass
                finally:
                    return
            try:
                if text_data.content_type == 'document':
                    code = get_file(session['args']['text_code'])
                else:
                    code = get_message(session['args']['text_code'])
                for delete_id in session['args']['delete_id']:
                    try:
                        bot.delete_message(chat_id=chat_id,
                                           message_id=delete_id)
                    except Exception:
                        pass
                send_document(chat_id, code)
            except Exception:
                pass
    except Exception as err:
        error(error_admin_text='Обработка сессий ' + str(err))
