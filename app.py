from datetime import datetime
from json import dumps

from flask import Flask, render_template, jsonify
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
import pandas as pd
import numpy as np

# Это просто нужно, для того, чтобы можно было отдавать данные
from flask_cors import CORS
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
def hello_world(product, qty, same_cat):

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

    #  Конвертируем в формат json
    analogs_json = jsonify({
        'product': str(product),
        'analogs': all_analogs_df.to_dict('records')
    })

    return analogs_json


print('test message')


# Получить данные пользователя
@app.route('/getactiveclients/')
def get_active_users():
    active_users = [{
            'username': user['username'],
            'name': user['name'],
            'telephone': user['telephone'],
            'email': user['email'],
            'quartile': user['quartile'],
            'favorite_shop': user['favorite_shop'],
            'favorite_shop_accepted': user['favorite_shop_accepted'],
            'Sity': user['Sity'],
        } for user in users
        if user['is_authorized']
    ]
    return(jsonify(active_users))

"""
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
"""

if __name__ == '__main__':
     app.run(port=5000)
