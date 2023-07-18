# Self-Service Bot 

Бот с двухфакторной аутентификацией зарегистрированных пользователей, который включает в себя алгоритм машинного обучения для поиска подходящих данных, сравнивая их с запросом пользователя.
## Зависимости

Зависимости в файле requirements.txt,можно установить с момощью pip:

`pip install -r requirements.txt `

Либо в ручную:

`pip install pyTelegramBotAPI`

`pip install numpy`

`pip install pandas`

`pip install torch`

`pip install transformers`

`pip install scikit-learn`

`pip install seaborn`

## Запуск
1) `python bot.py`

2) Необходимо загрузить тренировочные данные из сайта https://www.kaggle.com/datasets/dvorobiev/deeppavlov-rubertbasecased. Затем переименовывать загруженную папку на `deeppavlov-rubertbasecased` и подключить в файле bot.py 

3) *Дамп базы данных клиентов находится в папке `scr` customer.sql*

4) Папка Data содержит:
    - датасет в котором заранее сформированы запросы по url, search_keys
    - заранее приготовленные векторы полученные из датасета preprocessed_kb_base.csv
    - текстовый файл который временно будет хранить схожие запросы клиента

## 

*Логика бота и код алгоритма в **bot.py***
