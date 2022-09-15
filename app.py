from cmath import rect
import telebot
import sqlite3
import os
import math
import random
import smtplib,ssl

from telebot import types
TOKEN = ""

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    msg=bot.send_message(message.chat.id, "<b>Введите своё имя: </b>", parse_mode='html')
    bot.register_next_step_handler(msg, auth)

def auth(message):
    txt = message.text
    sqlite_connection = sqlite3.connect('consumer.sqlite')
    cursor = sqlite_connection.cursor()
    print("Подключен к SQLite")

    sqlite_select_query = f"SELECT * from customer where first_name = '{txt}' " 
    cursor.execute(sqlite_select_query)
    records = cursor.fetchall()
    if len(records)!=0:
        #print("Всего строк:  ", len(records))
        #print("Вывод каждой строки")
        for row in records:
            #print("ID:", row[0])
            #print("Имя:", row[1])
            #print("Фамилия:", row[2])
            #print("Почта:", row[3])
            #print("Статус:", row[4], end="\n\n")
            status = row[4]
            email = row[3]
            if status == 0:
                bot.send_message(message.chat.id, "<b>У вас нет доступа! ❌</b>", parse_mode='html')
                start(message)
            elif status == 1:
                msg=bot.send_message(message.chat.id, "<b>У вас есть доступ! ✅</b>\nВведите OTP: ", parse_mode='html') 
                digits="0123456789"
                global OTP
                OTP=""
                for i in range(6):
                    OTP+=digits[math.floor(random.random()*10)]
                otp = OTP + " is your OTP"
                otp_mess = otp
                port = 465  # For SSL 
                smtp_server = "smtp.gmail.com" 
                sender_email = "jasur.uzb10@gmail.com"  
                receiver_email = email  
                password = "" 
                context = ssl.create_default_context() 
                with smtplib.SMTP_SSL(smtp_server, port, context=context) as server: 
                    server.login(sender_email, password) 
                    server.sendmail(sender_email, receiver_email, otp_mess)
                bot.register_next_step_handler(msg, otp_check)   
    elif len(records)==0:
        bot.send_message(message.chat.id, "Вас нет в базе ‼️", parse_mode='html')
        start(message)
    cursor.close()

def otp_check(message):
    if OTP == message.text:
        msg=bot.send_message(message.chat.id, "Подтверждено ✅ \nЗадайте вопрос: ", parse_mode='html')
        bot.register_next_step_handler(msg, get_question)   
    else:
        bot.send_message(message.chat.id, "Не правильно❗️", parse_mode='html')

def get_question(message):
    bot.send_message(message.chat.id, "Идет загрузка... ", parse_mode='html')


bot.infinity_polling()

