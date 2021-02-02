from dotenv import load_dotenv
import os
import psycopg2
import datetime as date
from checks import negative_score_check

# Use environment variables from .env file
load_dotenv()

"""
Данные для подключения берем из .env файла, чтобы не хранить их в открытом
виде в коде. https://docs.repl.it/repls/secret-keys
"""
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    sslmode='require',
    host=os.getenv("DB_HOST"))

conn.autocommit = True


def get_game_id(game):
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM games WHERE game_name = (%(game)s);", {'game': game}
    )
    result = cur.fetchone()
    if result is None:
        return False
    return result[0]


def add_game_into_db(game):
    """
    Adding game to DB and return it's id (int) from table. If game already in
    db - pass this step and print error message
    """
    cur = conn.cursor()
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
    cur.execute(
        "SELECT id FROM games WHERE game_name = (%(game)s);", {'game': game}
    )
    return cur.fetchone()[0]


def add_users_into_db(score_pairs):
    """
    Adding seq of users to DB and return it's id from table. If user already
    in db - pass this step and print error message.
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT user_name FROM users"
    )
    present_users_list_raw = cur.fetchall()
    present_users_list_clean = []
    for elem in present_users_list_raw:
        present_users_list_clean.append(elem[0])
    for user in score_pairs.keys():
        if user in present_users_list_clean:
            print(f'{user} already in DB')
            continue
        else:
            cur.execute(
                "INSERT INTO users (user_name) VALUES (%(user)s);",
                {'user': user}
            )
            print(f'{user} added to DB')
    cur.execute(
        "SELECT id FROM users WHERE user_name IN %s;",
        (tuple([key for key in score_pairs.keys()]),)
    )
    return cur.fetchall()


def add_game_session_into_db(game_id):
    """
    Adding game_session to DB and return it's id from table
    :param game_id: from func add_game_into_db() from func parseMessage()
    :return: id (int) of current game_session from db
    """
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO game_sessions (created_at, game_id) "
        "VALUES (%(date)s, %(game_id)s);",
        {
            'date': date.datetime.now(),
            'game_id': game_id
        }
    )
    cur.execute(
        "SELECT id FROM game_sessions WHERE game_id = (%s);", (game_id,)
    )
    return cur.fetchall()[-1][0]


def add_scores(game, score_pairs):
    """
    Add scores to DB and return SUM of scores for current game in
    current game_session
    :param game: game to store
    :param score_pairs: pairs of players and scores
    :return: done string
    """
    try:
        negative_score_check(score_pairs)
    except ValueError:
        return "Negative score isn't possible"

    cur = conn.cursor()
    game_id = add_game_into_db(game)
    game_session_id = add_game_session_into_db(game_id)
    users_ids = add_users_into_db(score_pairs)
    result_msg_dict = dict()
    for user_id in users_ids:
        cur.execute(
            "SELECT user_name FROM users WHERE id = %s;", (user_id[0],)
        )
        user_name = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO scores VALUES (%(session_id)s, "
            "%(user_id)s, %(score)s);",
            {
                "session_id": game_session_id,
                "user_id": user_id[0],
                "score": score_pairs[user_name],
            }
        )
        cur.execute(
            'SELECT SUM(score) from scores WHERE '
            '(game_session_id in '
            '(SELECT id FROM game_sessions where game_id = %s) '
            'AND user_id = %s);',
            (game_id, user_id[0])
        )
        result_msg_dict[user_name] = int(cur.fetchone()[0])
    print(result_msg_dict)
    # return {'value1': str(result_msg_dict)}

    return result_msg_dict


def stats_represent(game):
    cur = conn.cursor()
    game_id = get_game_id(game)
    if not game_id:
        return 'В эту игру вы еще не шпилили'

    cur.execute('SELECT id FROM game_sessions WHERE game_id = %s;', (game_id,))
    game_sessions_ids = tuple(cur.fetchall())
    cur.execute(
        'SELECT user_id FROM scores WHERE game_session_id IN %s;',
        (game_sessions_ids,)
    )
    user_ids = tuple(set(cur.fetchall()))
    result_msg_dict = dict()
    for id in user_ids:
        cur.execute(
            "SELECT user_name FROM users WHERE id = %s;", (id[0],)
        )
        user_name = cur.fetchone()[0]
        cur.execute(
            'SELECT SUM(score) FROM scores '
            'WHERE game_session_id IN %s AND user_id = %s;',
            (game_sessions_ids, id)
        )
        result_msg_dict[user_name] = int(cur.fetchone()[0])
    return result_msg_dict
