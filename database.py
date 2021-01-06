import os
import psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    sslmode='require',
    host=os.getenv("DB_HOST"))

cur = conn.cursor()


def upsert_users():
    result = execute_values(cur,
                            'INSERT INTO games (game_name) VALUES %s ON CONFLICT (game_name) DO NOTHING RETURNING *;',
                            [('Сергей',), ('Егор',)], fetch=True)
    conn.commit()
    return result
