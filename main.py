import os
from replit import db
from flask import Flask
from flask import request
import requests


app = Flask('app')

@app.route('/', methods=['POST'])
def process_bot_message():
  """
  TODO Здесь приходит запрос вида {"value": "Червяки: Егор 1, Саша 5, Сергей 0"}. Нам нужно достать строку из value, и распарсить ее с помощью parse_message, чтобы можно было подготовить данные для запросов в базу данных.
  """
  return 'done'

  #request.get_json()
  
  
  # db["egor"] += int(request.form["egor"])
  # return str(db["egor"])




def post_response_to_telegram(data):
  """
  Когда мы подготовили все данные для отправки и сохранили их в базу данных, этой функцией можно послать ответ в Телеграм. Ответ здесь должен быть подготовленной строкой со вставленными данными  
  """

  requests.post(url=os.getenv("IFTTT_TELEGRAM_BOT_URL"), data=data)


#-----------------------------------------------------------------------------------------



@app.route('/stat', methods=['GET', 'POST'])
def income():
  result = {}
  if request.method == "GET":
    #    return dict(request.args) - dict from querystring
    #    return dict(request.args.lists()) - dict with multiple values for 'key'
    for key, value in request.args.items():
        #       INSERT INTO __table__ (__name_of_coloumn - keys, ...) VALUES(__value_of_coloumn__ - values, ...);
      result[key] = result.setdefault(key, 0) + int(value)
      db[key] = result[key]
  if request.method == "POST":
    users = ['egor', 'alex', 'sergio']
    for user in users:
      result[user] = request.form[user]
      db[user] = result[user]


  return str(db['egor'])


# request.post['Sergey']  - value for SERGEY in form

#------------------------------------------------------------------------------------------



# https://maker.ifttt.com/trigger/stats_updated/with/key/m8lqTaJGTj7KTRQK-cxwEg_C8n_a5MnIkae1FO1xRd8
# {value: 'Итого: Егор 1, Саша 5, Сергей 0'}

app.run(host='0.0.0.0', port=8080)


