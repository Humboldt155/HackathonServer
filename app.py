from datetime import datetime
from json import dumps

from random import randint

from flask import Flask, render_template, jsonify
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
import pandas as pd
import numpy as np

from flask import request

# Это просто нужно, для того, чтобы можно было отдавать данные
from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app)

from data import get_users
users = get_users()

#from sklearn.cluster import KMeans

# Импортируем базу данных всех товаров с указанием Наименований, Категорий и пр.
bdd_rms = pd.read_excel('library/BDD.xlsx', names=['product',
                                                   'department',
                                                   'model_adeo',
                                                   'model_name',
                                                   'date_created',
                                                   'product_name',
                                                   'is_stm'])

#################    Импортируем обученные модели   ####################

# Стандартная модель, обученная на артикулах
model_products = Word2Vec.load('models/w2v_64m_sg0_i220_window9_size160')

# Стандартная модель, обученная на моделях
model_categories = Word2Vec.load('models/w2v_64m_sg0_i220_window9_size160_Models')

# Модель для предложений по ближайшим покупкам (почему-то выдает ошибку, пока не открывать
#model_future_products = Word2Vec.load('models/w2v_64m_sg0_i220_window6_size150_lessAVS_during_2weeks')

conversations = {
        'client1': [
            {'type': ' ', 'author': ' ', 'data': {'text': ' '}}
        ],
        'client2': [
            {'type': ' ', 'author': ' ', 'data': {'text': ' '}}
        ],
        'client3': [
            {'type': ' ', 'author': ' ', 'data': {'text': ' '}}
        ],
        'client4': [
            {'type': ' ', 'author': ' ', 'data': {'text': ' '}}
        ]
}

users_conversations = {
        'client1': [
            {'type': ' ', 'author': ' ', 'data': {'text': ' '}}
        ],
        'client2': [
            {'type': ' ', 'author': ' ', 'data': {'text': ' '}}
        ],
        'client3': [
            {'type': ' ', 'author': ' ', 'data': {'text': ' '}}
        ],
        'client4': [
            {'type': ' ', 'author': ' ', 'data': {'text': ' '}}
        ]
}



# Приветствие
@app.route('/')
def hello_team():
    return 'Hello, Team!'


# Запрос на аналоги
""" Принимает параметры: 
        product (артикул, в формате string), 
        qty (Максимум аналогов, int), 
        same_cat (0 - товар из любой категории. 1 - товар из той же категории)
"""
@app.route('/analogs_product/<int:product>/<int:qty>/<int:same_cat>')
def get_analogs_product(product, qty, same_cat):

    koef = 1          # Если требуются артикулы из той же категории, стоит запросить больше аналогов
    if same_cat == 1:
        koef = koef*3

    #  Получаем датафрейм с аналогами
    all_analogs = model_products.most_similar(str(product), topn=qty*koef)

    # Конвертируем в pandas DataFrame
    all_analogs_df = pd.DataFrame(all_analogs, columns=['product', 'probability'])
    all_analogs_df['product'] = all_analogs_df['product'].astype('int64')

    # Подтягиваем категорию и название
    all_analogs_df = all_analogs_df.merge(bdd_rms, on='product')

    all_analogs_df['product_url'] = "https://res.cloudinary.com/lmru/image/upload/w_130,h_130,c_pad,b_white,d_photoiscoming.png/LMCode/" + all_analogs_df['product'].astype(str) + ".jpg"
    all_analogs_df['product_quartile'] = 2  # Не забыть убрать
    all_analogs_df['product_price'] = 278  # Не забыть убрать
    all_analogs_df = all_analogs_df.to_dict('records')

    for i in range(0, len(all_analogs_df)):
        all_analogs_df[i]['stock'] = {'online': 0, 'clients_store': 0, 'clients_sity': 0}

    #  Конвертируем в формат json
    analogs_json = jsonify({
        'product': str(product),
        'analogs': all_analogs_df
    })

    return analogs_json


print('test message')

# Получить данные артикула
@app.route('/getproduct/<int:product>')
def get_product(product):
    product_df = bdd_rms[bdd_rms['product'] == product]
    product_df['product_url'] = "https://res.cloudinary.com/lmru/image/upload/w_170,h_170,c_pad,b_white,d_photoiscoming.png/LMCode/" + product_df['product'].astype(str) + ".jpg"
    product_df['product_quartile'] = 2
    product_df['product_price'] = 765
    product_df = product_df.to_dict('records')[0]
    product_df['stock'] = {'online': 0, 'clients_store': 0, 'clients_sity': 0}
    return(jsonify(product_df))

@app.route('/get_chats/')
def get_chats():
    return(jsonify(conversations))

@app.route('/get_user_chat', methods=['GET'])
def get_user_chat():
    return(jsonify(users_conversations[request.args['user']]))



@app.route('/send_message', methods=['GET'])
def send_message():
    user = request.args['user']
    author = request.args['author']
    type = request.args['type']
    name = request.args['name']
    price = request.args['price']
    code = request.args['code']
    if user == 'me':
       user = author
    conversations[user].append(
        {
            'type': type,
            'author': author,
            'data': {
                 'text': name,
                 'name': price,
                 'url': code
             }
         }
        )
    if author == user:
        author = 'me'
    else:
        author = 'assistant'
    users_conversations[user].append(
        {
            'type': type,
            'author': author,
            'data': {
                'text': name,
                'name': price,
                'url': code
            }
        }
    )
    return(jsonify({'response': 'hello'}))

if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000) # Запуск на удаленном сервере
    app.run(port=5000)                 # Запуск на локальном сервере сервере
