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

# ---------------------------------------------
# {"value": "Червяки: Егор 1, Саша 5, Сергей 0"}
# parse.parseMessage()  - [0] - game_name, [1] - dict_with_stats

incoming_message = {'value': 'Basket: Bari 500, Sergio 100, Julia 200'}

game = parse.parse_message(incoming_message)[0]
scores_dict = parse.parse_message(incoming_message)[1]


# Для добавление строки в таблицы gamers и games необходимо проверить является ли игра/игрок новыми для БД. Для этого используем "множества"

# https://stackoverflow.com/questions/5247685/python-postgres-psycopg2-getting-id-of-row-just-inserted


def add_game_into_db(game):
    """
    Adding game to DB and return it's id (int) from table. If game already in db - pass this step and print error message
    """
    try:
        cur.execute("INSERT INTO games (game_name) VALUES (%(game)s);", {'game': game})
        conn.commit()
    except:
        print('game already in DB')
        conn.commit()
    cur.execute("SELECT id FROM games WHERE game_name = (%(game)s);", {'game': game})
    return cur.fetchone()[0]


def add_users_into_db(users: dict):
    """
    Adding seq of users to DB and return it's id from table. If user already in db - pass this step and print error
    message.
    """
    for user in users.keys():
        try:
            cur.execute("INSERT INTO users (user_name) VALUES (%(user)s);", {'user': user})
            print(f'{user} added to DB')
        except:
            print(f'{user} already in DB')
        finally:
            conn.commit()
    cur.execute("SELECT id FROM users WHERE user_name IN %s;", (tuple([key for key in users.keys()]),))
    return cur.fetchall() # ЗДЕСЬ ВОЗВРАЩАЕТСЯ ПОСЛЕДОВАТЕЛЬНОСТЬ ID ПО ВОЗРАСТАНИЮ


def add_game_session_into_db(game_id):
    """
    Adding game_session to DB and return it's id from table
    :param game_id: from func add_game_into_db() from func parseMessage()
    :return: id (int) of current game_session from db
    """
    cur.execute(
        "INSERT INTO game_sessions (created_at, game_id) VALUES (%(date)s, %(game_id)s);",
        {
            'date': date.datetime.now(),
            'game_id': game_id
        }
    )
    conn.commit()
    cur.execute("SELECT id FROM game_sessions WHERE game_id = (%s);", (game_id,))
    return cur.fetchall()[-1][0]

def add_scores(game_session_id, users_id, scores):
    """
    Adding score to DB and return SUM of scores for current game
    :param user_id: from func add_users_into_db() from func parseMessage()
    :return: id of current game_session from db
    """
    for id, user_name in zip(users_id, scores.keys()):#TODO сопоставления двух последовательностей, т.к. users_id возвращается из add_users ВСЕГДА в порядке возрастания, a scores.keys - из распарсенного сообщения как есть!!
        cur.execute(
            "INSERT INTO scores (game_session_id, user_id, score) VALUES (%(session_id)s, %(user_id)s, %(score)s);",
            {
                "session_id": game_session_id,
                "user_id": id[0],
                "score": scores[user_name],
            }
        )
        conn.commit()