import os
import psycopg2
import parse_message
from flask import request
import datetime as date
"""
Данные для подключения берем из .env файла, чтобы не хранить их в открытом виде в коде. https://docs.repl.it/repls/secret-keys
"""
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    sslmode='require',
    host=os.getenv("DB_HOST"))

cur = conn.cursor()

cur.execute("SELECT score, game_session_id FROM scores;")

print(cur.fetchall())

#---------------------------------------------
# {"value": "Червяки: Егор 1, Саша 5, Сергей 0"}
# parse.parseMessage()  - [0] - game_name, [1] - dict_with_stats

game_name = parse_message.parse(request.form['value'])[0]
stats = parse_message.parse(request.form['value'])[1]

# Для добавление строки в таблицы gamers и games необходимо проверить является ли игра/игрок новыми для БД. Для этого используем "множества"

# https://stackoverflow.com/questions/5247685/python-postgres-psycopg2-getting-id-of-row-just-inserted


games = []
gamers = []
games_session = []

if game_name not in games:
	games.append(game_name)
	cur.execute("INSERT INTO games (name) VALUE (%s)", (game_name))

for gamer in stats.keys():
	if gamer not in gamers:
		gamers.append(gamer)
		cur.execute("INSERT INTO gamers (name) VALUE (%s)", (gamer))

cur.execute(
    "INSERT INTO game_session (created_at, game_id) VALUES (%s, %s)",
    (date.datetime.now(), games.index(game_name) + 1)
)  # сложность с автоматизацией записи id игры в связанную таблицу game_session. Нужно или помомнить id игры или использовать словарь/кортеж с индексами из enumerate/[].index из списка +1 (индексация начинается с 0)/

# Как увязать id сессии с конкретным сеансом записи статистик в scores?
for gamer in stats.keys():
	cur.execute(
	    "INSERT INTO scores (game_session_id, user_id, scores) VALUES (%s, %s, %s)",
	    (
	        # session_id??,
	        gamers.index(gamer) + 1,
	        stats[gamer]))
