import os
import psycopg2

"""
Данные для подключения берем из .env файла, чтобы не хранить их в открытом виде в коде. https://docs.repl.it/repls/secret-keys
"""
conn = psycopg2.connect(
  dbname=os.getenv("DB_NAME"), 
  user=os.getenv("DB_USER"),
  password=os.getenv("DB_PASSWORD"),
  sslmode='require', host=os.getenv("DB_HOST"))

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