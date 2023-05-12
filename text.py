"""
Модуль содержит тексты для сообщений

"""

import texttable as table

import admin
import mongodb as backend


def greeting():
    """
    :return: текст-приветствие

    """
    text = 'Welcome to the <b>TextSaver</b> bot!\n\n'
    text += '<i>If you need help, press /help</i>\n'
    return text


def menu():
    """
    :return: текст для меню

    """

    text = 'How can I help you?'
    return text


def send_code():
    """
    :return: текст для отправки нового кода

    """
    text = 'Send me the desired Text in the message below, please.\n\n' \
           '<i>❗️If the original text is not completely converted, ' \
           'then it may be too large to read from the message. ' \
           'Try to send it as a file.</i>\n\n' \
           '<i>To cancel the action press /cancel.</i>'
    return text


def text_info(text_code, user_text=None):
    """
    :return: информация о тексте

    """
    try:
        if user_text is None:
            user_text = backend.get_text(text_code)
        if user_text is None:
            text = 'Sorry, something went wrong.'
            return text
        text = '*Title:* ' + user_text['name'] + '\n'
        text += '*Date*: ' + user_text['beautiful_date'] + '\n'
        if user_text:
            text += '*Size*: ' + str(int(user_text['bytes']) // 1024) + ' KB\n\n'
        text += f'[Link]({user_text["link"]})'
        text += '\n_(copy the link to share this text with someone)_\n\n'
        return text
    except Exception as err:
        admin.error(error_admin_text='Не получилось содздать описание текста' + str(err))
        return None


def cant_parse_text():
    """
    :return: извинения за то, что не получается запарсить текст из файла
    Попросить отправить текст в другом формате

    """
    text = 'Sorry, I can\'t read the Text from your file.\n'
    text += 'Try to send me the desired Text again in a different format.\n'
    return text


def my_texts(chat_id, first=0, user=None):
    """
    :param chat_id: id пользователя
    :param first: номер первого файла на странице
    :param user: информация о пользователе
    :return: все тексты пользователя

    """
    try:
        if user is None:
            user = backend.get_user(chat_id)

        text = '<i>Occupancy of your storage:\n' + \
               str(user['used_memory'] // 1024) \
               + '/' \
               + str(user['max_memory'] // 1024) + ' KB.</i>\n\n'

        if len(user['texts']) == 0:
            text += 'You have no saved Texts.'
            return text
        text += 'Send the desired number of text.\n\n'
        texts = table.Texttable()
        texts.set_deco(table.Texttable.HEADER)
        texts.set_cols_align(["l", "c", "c"])
        texts.set_cols_valign(["m", "m", "m"])
        texts.set_cols_dtype(['i', 't', 't'])
        texts.add_row(["№\n", "Title\n", "Date\n"])
        top = first + 1
        codes = []
        for i in range(first, min(len(user['texts']), first + 15)):
            codes.append(backend.get_text(user['texts'][i]))
        for user_text in codes:
            try:
                if user_text is not None:
                    text_name = user_text['name']
                    if len(text_name) > 10:
                        text_name = text_name[: 10] + '...'
                    texts.add_row([top, text_name, user_text['date']])
            except Exception as err:
                admin.error(error_admin_text='No Text ' + str(err))
            top += 1

        text += '<pre>' + texts.draw() + '</pre>'
        return text
    except Exception as err:
        admin.error(error_admin_text='Создание текста my_texts ' + str(err))
        return None


def confirmation_text_deletion():
    """
    :return: Подтверждение удаления текста

    """
    text = 'Do you want to delete this Text?'
    return text


def change_title():
    """
    :return: Изменение названия файла

    """
    text = 'Send me the desired Text title.\n\n' \
           '<i>To cancel the action press /cancel.</i>'
    return text


def cant_output_text():
    """
    :return: Нельзя вывести текст в этом формате

    """
    text = "Unfortunately, I can\'t send Text in this format."
    return text


def warning_delete():
    """
    :return: предупреждение о том, что текст удалится, если его не сохранить

    """
    text = "_If the author of the Text deletes it, " \
           "you will lose access to it. " \
           "To avoid this, you can save the Text to yourself._"
    return text


def text_deleted():
    """
    :return: текст удалён

    """
    text = "The Text has been deleted by its author."
    return text


def settings():
    """

    :return: текст с настройками
    """
    text = 'Choose which file format will be displayed by default ' \
           'in the message with information about the Text.'
    return text


def wait():
    """
    :return: текст с ожиданием

    """
    text = 'Wait, please 🕒'
    return text


def file_is_large():
    """
    :return: текст с оповещением о том, что файл слишком большой для отправки

    """
    text = "Sorry, I have a file size limit of up to 2 MB."
    return text


def file_is_large_for_storage():
    """
    :return: текст с оповещением о том, что файл слишком большой для хранилища

    """
    text = "Sorry, this Text is too large for your storage.\n" \
           "Remove any Text to free up your memory."
    return text


def title_is_large():
    """
    :return: текст с оповещением о том, что название файла слишком большое

    """
    text = "The file title must be up to 30 characters long."
    return text


def payment():
    """
    :return: текст с информацией об оплате Premium режима.

    """
    text = "Premium mode will expand your storage up to 10MB."
    return text


def help():
    """
    :return: текст для /help

    """
    text = '*__TextSaver__*\n' \
           'TextSaver bot can create and store Texts, and allows you to share them with someone\.\n\n'
    text += '*__Create Text__*\n' \
            'To display the main menu, press the *TextSaver* button on the keyboard at the bottom of the screen\.\n' \
            'To create and save Text, press *Create Text* and then send your text in one of the following formats:\n' \
            '1\. _File_ \- The bot will try to read the text from the file you have sent\. If he fails, he will notify\.\n' \
            '2\. _Telegram message_ \- Send text up to 4096 characters with a message in Telegram\.\n\n'
    text += '*__Storage__*\n' \
            'The generated Texts are automatically saved in your storage\. ' \
            'You can view the contents of this storage by pressing *MyTexts*\. ' \
            'The storage size is 2 MB\.\n\n'
    text += '*__Text Information__*\n' \
            'Clicking on the Text will return the information about it\.\n' \
            'By default, you will see the pdf file with the Text\. ' \
            'If the pdf file can\'t be created, the txt file will be sent to you\. ' \
            'If you want to configure the default output of the txt file, press /settings\.\n\n'
    text += '*__You can also__*\n' \
                'Change the Text title \(*Title*\)\n' \
                'Edit the Text content \(*Edit*\)\n' \
                'Display the Text in txt format \(*\.txt*\)\n' \
                'Display the Text in pdf format \(*\.pdf*\)\n' \
                'Display the Text with a message in Telegram \(*\.tg*\)\n' \
                'Delete the Text \(*Delete*\)\n\n'
    text += '*__Text Link__*\n' \
            'Each Text has its own *link*, which you can find in the information about the Text\. ' \
            'You can send this link to someone\. ' \
            'A person will be able to see your Text and save it to himself\.\n' \
            'If you update the Text content, ' \
            'the person will be able to press *Update* and see the updated Text\.\n' \
            'If you delete the Text and the person hasn\'t saved it, he will lose access to the Text\.'
    return text


def stats():
    try:
        table_stats = table.Texttable()
        table_stats.set_deco(table.Texttable.HEADER)
        table_stats.set_cols_align(["l", "c"])
        table_stats.set_cols_valign(["m", "m"])
        table_stats.set_cols_dtype(['t', 'i'])
        db_stats = backend.get_stats()
        for key, value in db_stats.items():
            table_stats.add_row([key, value])

        text = '<b>Statistics:</b>\n\n'
        text += '<pre>' + table_stats.draw() + '</pre>'
        return text
    except Exception as err:
        admin.error(error_admin_text='Создание текста stats ' + str(err))
        return None
