from database import updated_add_game_into_db

GAME_NAME = 'Apex'


def test_add_game(postgres):
    cursor = postgres.cursor()
    updated_add_game_into_db(cursor, GAME_NAME)
    cursor.execute("SELECT * FROM games;")
    result = cursor.fetchone()
    cursor.close()
    assert result[1] == GAME_NAME


def test_add_duplicate_game(postgres):
    cursor = postgres.cursor()
    updated_add_game_into_db(cursor, GAME_NAME)
    updated_add_game_into_db(cursor, GAME_NAME)
    cursor.execute("SELECT * FROM games;")
    results = cursor.fetchall()
    cursor.close()
    assert len(results) == 1
