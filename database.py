import os
import psycopg2
import parse_message as parse
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
"""
CREATE TABLE games (
	id BIGINT PRIMARY KEY generated always as identity,
	game_name VARCHAR(255));

CREATE TABLE users (
	id BIGINT PRIMARY KEY generated always as identity,
	user_name VARCHAR(255));

CREATE TABLE game_sessions (
	id BIGINT PRIMARY KEY generated always as identity,
	created_at TIMESTAMP,
	game_id BIGINT REFERENCES games);

CREATE TABLE scores (
	game_session_id BIGINT REFERENCES game_sessions,
	user_id BIGINT REFERENCES users,
	score BIGINT);

INSERT INTO users (user_name) VALUES ('Sergey'), ('Egor'), ('Sasha');

INSERT INTO games (game_name) VALUES ('Chervaki');

INSERT INTO game_sessions (game_id, created_at) VALUES (1, '2021-01-03 10:10:10+1');

INSERT INTO scores (game_session_id, user_id, score) VALUES (1, 1, 2), (1, 2, 1), (1, 3, 4);

INSERT INTO game_sessions (game_id, created_at) VALUES (1, '2021-01-01 14:12:36+1');

INSERT INTO scores (game_session_id, user_id, score) VALUES (2, 1, 5), (2, 2, 3), (2, 3, 1);

SELECT SUM(score) FROM scores WHERE user_id = 1;
"""

#---------------------------------------------
# {"value": "Червяки: Егор 1, Саша 5, Сергей 0"}
# parse.parseMessage()  - [0] - game_name, [1] - dict_with_stats

game_name = parse.parse_message(request.form['value'])[0]
stats = parse.parseMessage(request.form['value'])[1]

# Для добавление строки в таблицы gamers и games необходимо проверить является ли игра/игрок новыми для БД. Для этого используем "множества"

# https://stackoverflow.com/questions/5247685/python-postgres-psycopg2-getting-id-of-row-just-inserted


def counter():
	pass


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
