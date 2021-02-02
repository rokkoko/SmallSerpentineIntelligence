from flask import Flask
from flask import request
from parse_message import parse_message
from database import add_scores, stats_represent
import json
import requests
import datetime as date

IFTTT_TELEGRAM_BOT_URL = 'https://maker.ifttt.com/' \
                         'trigger/stats_updated/with/' \
                         'key/m8lqTaJGTj7KTRQK-cxwEg_C8n_a5MnIkae1FO1xRd8'


def create_app():
    app = Flask('stats')

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
            try:
                game, score_pairs = parse_message(data)
            except (ValueError, TypeError):
                game = parse_message(data)
                score_pairs = stats_represent(game)
                if isinstance(score_pairs, str):
                    no_such_game_msg = score_pairs
                    post_response_to_telegram(no_such_game_msg)
                    return 'Done!'
                elif isinstance(score_pairs, dict):
                    result_dict = score_pairs
                    case = 'общие статы ВСЕХ игрокококов такие'
            else:
                result_dict = add_scores(game, score_pairs)
                case = 'статы для текущих игрококов'
                if isinstance(result_dict, str):
                    negative_score_msg = result_dict
                    post_response_to_telegram(negative_score_msg)
                    return 'Done!'

            app.logger.debug('Parsed message', game, score_pairs)

            result_msg = f'На {date.datetime.today().replace(microsecond=0)} ' \
                         f'по игре "{game}" {case}:\n'
            for user_name, score in result_dict.items():
                result_msg += user_name + ': ' + str(score) + '\n'

            post_response_to_telegram(result_msg)

            return 'Done!'

    def post_response_to_telegram(data):
        """
        Когда мы подготовили все данные для отправки и сохранили их в базу
        данных, этой функцией можно послать ответ в Телеграм. Ответ здесь
        должен быть подготовленной строкой со вставленными данными
        """
        requests.post(url=IFTTT_TELEGRAM_BOT_URL, data={"value1": data})

    return app


# We need this for test not to run server, only main process will run it
if __name__ == "__main__":
    server_app = create_app()

    server_app.run(host='0.0.0.0', port=7001)
