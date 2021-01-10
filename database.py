from dotenv import load_dotenv
import os
import psycopg2
import parse_message as parse
from flask import request
import datetime as date

# Use environment variables from .env file
load_dotenv()

"""
Данные для подключения берем из .env файла, чтобы не хранить их в открытом виде в коде. https://docs.repl.it/repls/secret-keys
"""
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    sslmode='require',
    host=os.getenv("DB_HOST"))

conn.autocommit = True




# ---------------------------------------------
# {"value": "Червяки: Егор 1, Саша 5, Сергей 0"}
# parse.parseMessage()  - [0] - game_name, [1] - dict_with_stats

incoming_message = {'value': 'Basket: Bari 500, Sergio 100, Julia 200'}

game = parse.parse_message(incoming_message)[0]
scores_dict = parse.parse_message(incoming_message)[1]


def add_game_into_db(game, cur=conn.cursor()):
    """
    Adding game to DB and return it's id (int) from table. If game already in db - pass this step and print error message
    """
    cur.execute(
        "SELECT game_name FROM games"
    )
    present_games_list_raw = cur.fetchall()
    present_games_list_clean = []
    for elem in present_games_list_raw:
        present_games_list_clean.append(elem[0])
    if game in present_games_list_clean:
        print(f'game {game} already in DB')
    else:
        cur.execute(
            "INSERT INTO games (game_name) VALUES (%(game)s);", {'game': game}
        )
    cur.execute("SELECT id FROM games WHERE game_name = (%(game)s);", {'game': game})
    return cur.fetchone()[0]

game_id = add_game_into_db(game)


def add_users_into_db(users: dict, cur=conn.cursor()):
    """
    Adding seq of users to DB and return it's id from table. If user already in db - pass this step and print error
    message.
    """
    cur.execute(
        "SELECT user_name FROM users"
    )
    present_users_list_raw = cur.fetchall()
    present_users_list_clean = []
    for elem in present_users_list_raw:
        present_users_list_clean.append(elem[0])
    for user in users.keys():
        if user in present_users_list_clean:
            print(f'{user} already in DB')
            continue
        else:
            cur.execute("INSERT INTO users (user_name) VALUES (%(user)s);", {'user': user})
            print(f'{user} added to DB')
    cur.execute("SELECT id FROM users WHERE user_name IN %s;", (tuple([key for key in users.keys()]),))
    return cur.fetchall()


def add_game_session_into_db(game_id, cur=conn.cursor()):
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
    cur.execute("SELECT id FROM game_sessions WHERE game_id = (%s);", (game_id,))
    return cur.fetchall()[-1][0]

def add_scores(game_session_id, users_id, scores, game_id, cur=conn.cursor()):
    """
    Add scores to DB and return SUM of scores for current game in current game_session
    :param game_session_id: from func add_game_session_into_db()
    :param users_id: from func add_users_into_db()
    :param scores: from func parseMessage()
    :param game_id: from func parseMessage()
    :return: dict-type message with stats for users in game from income-message. Print message.
    """
    result_msg_dict = dict()
    for id in users_id:
        cur.execute(
            "SELECT user_name FROM users WHERE id = %s;", (id[0],)
        )
        user_name = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO scores VALUES (%(session_id)s, %(user_id)s, %(score)s);",
            {
                "session_id": game_session_id,
                "user_id": id[0],
                "score": scores[user_name],
            }
        )
        cur.execute(
            "SELECT SUM(score) from scores WHERE (game_session_id in (SELECT id FROM game_sessions where game_id = %s) AND user_id = %s);", (game_id, id[0])
        )
        result_msg_dict[user_name] = int(cur.fetchone()[0])
    print(result_msg_dict)
    return {'value1': str(result_msg_dict)}

add_scores(add_game_session_into_db(game_id), add_users_into_db(scores_dict), scores_dict, game_id)