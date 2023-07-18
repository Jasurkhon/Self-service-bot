from cmath import rect
import telebot
import sqlite3
import os
import math
import random
import smtplib,ssl


import numpy as np
import pandas as pd
import torch
import re
import torch
from tqdm import notebook
from itertools import combinations
from transformers import AutoTokenizer, AutoModel

from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import cdist, cosine
from scipy.stats.stats import pearsonr

from sklearn.cluster import KMeans
import seaborn as sns
import matplotlib.pyplot as plt

from telebot import types
TOKEN = "5652255226:AAEvRkApv54XhIKBGtvw4-eLFu6q6g4EzJU"

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
        for row in records:
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
                password = "zrlmvhmejfvgxztn" 
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
        resend_otp(message)
        #bot.register_next_step_handler(msg, resend_otp) 

def resend_otp(message):
    msg=bot.send_message(message.chat.id, "Отправьте OTP заново!", parse_mode='html')
    bot.register_next_step_handler(msg, otp_check)

def get_question(message):
    
    get_text = message.text
    
    bot.send_message(message.chat.id, "Идет загрузка... ", parse_mode='html')
    
    BERT = 'deeppavlov-rubertbasecased'
    # для исследования берем все встроки из датасета (их 1594)
    df_search = pd.read_csv('./Data/preprocessed_kb_base.csv', encoding='utf8')[['url', 'search_keys']][:1594]
    
    # загружаем два алгоритма
    # токенайзер - инструмент перевода слов в токены - числовые значения слов в словаре 
    # и модель превращения вектора с токенами в эмбеддинги

    tokenizer = AutoTokenizer.from_pretrained(BERT)
    model = AutoModel.from_pretrained(BERT)

    # переносим названия статей из колонки датафрейма в список и приводим все слова в нижний регистр
    corpus = df_search['search_keys'].str.lower().values
    
    #загружаем ранее созданные эмбеддинги(запросы клиентов из датасета 'preprocessed_kb_base.csv') из файла NewVec.npy
    results = np.load('./Data/NewVec.npy', allow_pickle=True)
    embeddings = results

    
    # ищем похожие статьи по тексту из запроса пользователя
    corpus_from_user = []
    text = get_text
    
    # удаляем из текста ненужные знаки препинания
    text = re.sub(r'\xa0', ' ', text)
    text = re.sub(r'«»,:', '', text)
    corpus_from_user.append(text)

    # переводим предложение в векторы
    # каждому слову соответсвует определеное число в словаре
    tokenized = []
    for i in corpus_from_user:
        tokenized.append(tokenizer.encode(i, add_special_tokens=True))

    # рассчитываем максимальную длину маски внимания
    max_len = 0
    for i in tokenized:
        if len(i) > max_len:
            max_len = len(i)

    # для каждого токенизированного предложения создаем маску внимания и приводим векторы к единой длине
    padded = np.array([i + [0]*(max_len - len(i)) for i in tokenized])
    attention_mask = np.where(padded != 0, 1, 0)

    # сколько предложений будет обработано за одну итерацию
    batch_size = 1

    # c помощью модели BERT переводим токенизированные предложения в эмбеддинги
    embeddings_find = []
    for i in notebook.tqdm(range(padded.shape[0] // batch_size)):
            batch = torch.LongTensor(padded[batch_size * i : batch_size * (i + 1)]) 
            attention_mask_batch = torch.LongTensor(attention_mask[batch_size * i : batch_size * (i + 1)])

            with torch.no_grad():
                batch_embeddings = model(batch, attention_mask=attention_mask_batch)

            embeddings_find.append(batch_embeddings[0][:,0,:].numpy())
    
    
    # выбираем пример заданный пользователем, относительно которого будем подбирать похожие запросы
    example = embeddings_find[0]

    # два списка, в которые будем отбирать претендетов на показ
    idx = []
    cos_sim = []

    # пробегаемся списком по всем эмбеддингам и выбираем те, где косинусное расстояние от образца менее 15%. 
    # или где косинусная схожесть больше или равна 85%
    for i, j in enumerate(embeddings):
        if cosine_similarity(example, j) >= 0.85:
            idx.append(i)
            cos_sim.append(cosine_similarity(example, j)[0][0])

    # собираем все найденные заголовки в новый датафрейм, добавляем конисусное расстояние и выводим топ-11 подобных заголовков
    # заголовок со схожестью 1 - образец
    cos_sim = pd.Series(cos_sim, name='cos_sim', index=idx)
    res = df_search.query('index in @idx').copy()
    res = res.join(cos_sim)
    res = res.sort_values(by='cos_sim', ascending=False)[:11]
    
    # выбираем 'url', 'search_keys' столбцов в кадре данных pandas и сохраняем в файл для отправки пользователю 
    r=res.loc[:, 'url':'search_keys']
    np.savetxt(r'./Data/np.txt', r.values, fmt='%s')
    new_list = []
    with open("./Data/np.txt", 'r') as file:
         new_list = file.read()
    
    send_result = "Подходящие запросы похожие с вашим запросом:\n"+new_list
    get_query = "Ваш запрос:\n"+ text
    
    bot.send_message(message.chat.id, get_query, parse_mode='html')
    bot.send_message(message.chat.id, send_result, parse_mode='html')
    #res
    #bot.send_message(message.chat.id, res, parse_mode='html')
bot.infinity_polling()








