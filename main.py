from flask import Flask
from flask import request
from parse_message import parse_message
from database import add_scores
import json
import requests

IFTTT_TELEGRAM_BOT_URL = 'https://maker.ifttt.com/' \
                         'trigger/stats_updated/with/' \
                         'key/m8lqTaJGTj7KTRQK-cxwEg_C8n_a5MnIkae1FO1xRd8'

def create_app():
    app = Flask('stats')

    # TODO Здесь приходит запрос вида
    #  {"value": "Червяки: Егор 1, Саша 5, Сергей 0"}. Нам нужно достать
    #  строку из value, и распарсить ее с помощью parse_message,
    #  чтобы можно было подготовить данные для запросов в базу данных.
    @app.route('/webhooks/stats', methods=['POST'])
    def process_bot_message():
        """
        Get stats data from incoming request body (sent by bot)
        and store it in database
        """

        app.logger.debug('Incoming bot request')

        if request.method == "POST":
            data = request.json
            app.logger.debug('Got data', json.dumps(data))

            game, score_pairs = parse_message(data)
            app.logger.debug('Parsed message', game, score_pairs)

            result = add_scores(game, score_pairs)

            post_response_to_telegram(result)

            return 'Done'

    def post_response_to_telegram(data):
        """
        Когда мы подготовили все данные для отправки и сохранили их в базу
        данных, этой функцией можно послать ответ в Телеграм. Ответ здесь
        должен быть подготовленной строкой со вставленными данными
        """
        requests.post(url=IFTTT_TELEGRAM_BOT_URL, data={"value1": str(data)})

    return app


# We need this for test not to run server, only main process will run it
if __name__ == "__main__":
    server_app = create_app()

    server_app.run(host='0.0.0.0', port=7001)
