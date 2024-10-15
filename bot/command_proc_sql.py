import os
from telegram import Update
import psycopg2
from telegram.ext import CallbackContext, ConversationHandler
import csv
import io

def runSQLSelect(command):
    try:

        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),  # IP-адрес или доменное имя удалённого сервера
            database=os.getenv('DB_DATABASE'),  # Имя базы данных
            user=os.getenv('DB_USER'),  # Имя пользователя PostgreSQL
            password=os.getenv('DB_PASSWORD'),  # Пароль
            port=os.getenv('DB_PORT')  # Порт PostgreSQL, по умолчанию 5432
        )
        cursor = connection.cursor()
        cursor.execute(command)
        records = cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        er = "Ошибка при подключении к PostgreSQL" + str(error)
        print (er)
        return er
    

    # Закрываем курсор и соединение с базой данных
    if connection:
        cursor.close()
        connection.close()

    if not records:
        print("Запрос вернул пустую таблицу.")
        return "Запрос вернул пустую таблицу."

    data = ""
    for i, record in enumerate(records):
        data = data + f"{i+1}. {record[1]}\n"
    return data


def runSQLInsert(command, data):
    try:

        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_DATABASE'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT')
        )
        cursor = connection.cursor()
        cursor.executemany(command, data)
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Ошибка при подключении к PostgreSQL", error)
        return False

    # Закрываем курсор и соединение с базой данных
    if connection:
        cursor.close()
        connection.close()
    return True


def getReplLogsCommand(update: Update, context):
    connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_DATABASE'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT')
    )
    csv_file_path = '/var/log/postgresql/db.csv'
    cursor = connection.cursor()
    output = io.StringIO()
    cursor.execute(f"SELECT pg_read_file('{csv_file_path}')")
    output = cursor.fetchall()[0][0]
    #output.replace(",", " ")

    # csv_data = output.getvalue()
    # reader = csv.reader(csv_data.splitlines())
    # header = next(reader)
    # result = ""
    # for row in reader:
    #     result += row
    update.message.reply_text(output.replace(",", " "))



def writeData(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    callback_data = query.data

    data = context.user_data.get(callback_data, [])
    if data:
        if callback_data == "phone": sqlquery = f"insert into phone (phone_number) values (%s);"
        elif callback_data == "email": sqlquery = f"insert into mail (email) values (%s);"
        res = [[numb] for numb in data]
        stdout = runSQLInsert(sqlquery, res)
        if stdout:
            query.edit_message_text(text="Данные успешно записаны")
        else:
            query.edit_message_text(text="Данные не записаны. Ошибка.")
    else:
        query.edit_message_text(text="Данные не найдены")

    context.user_data.clear()
    return ConversationHandler.END


def getEmailsCommand(update: Update, context):
    message = runSQLSelect("select * from mail")
    update.message.reply_text(message)


def getPhoneNumbersCommand(update: Update, context):
    message = runSQLSelect("select * from phone")
    update.message.reply_text(message)