# Телеграмм-бот TextSaver

Этот проект содержит исходный код телеграмм-бота TextSaver.
Функциональным назначением бота является хранение текстовых файлов, 
отправленных пользователем, с предоставлением возможности конвертации в 
.pdf и .txt форматы, а также последующим редактированием. 
Бот также даёт возможность делиться текстовыми файлами с другими пользователями Telegram. 
В качестве аналогов, реализованных в виде веб-сайтов, можно привести GitHubGist, pastebin. 
Для хранения данных использовалась база данных MongoDB.

Как запустить бота:
1. Создайте нового бота в Telegram, следуя инструкциям на официальном сайте Telegram
2. Получите токен вашего бота, запишите его в файл const.py в соответствующее поле TOKEN
3. Зарегистрируйтесь в MongoDB Atlas для создания облачной базы MongoDB
4. В файле const.py введите необходимую информацию для подключения к БД
5. В переменной admins укажите user_id администраторов бота
6. В переменной GROUP_ID укажите chat_id для отправки логов и ошибок в канал
7. Установите необходимые библиотеки, запустив команду pip install -r requirements.txt.
8. Запустите бота, выполнив команду python main.py.