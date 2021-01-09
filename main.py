from flask import Flask
from flask import request


# We use this function to create app instance for tests
def create_app():
    app = Flask('stats')

    # TODO Здесь приходит запрос вида {"value": "Червяки: Егор 1, Саша 5, Сергей 0"}. Нам нужно достать строку из value,
    #  и распарсить ее с помощью parse_message, чтобы можно было подготовить данные для запросов в базу данных.
    @app.route('/webhooks/stats', methods=['POST'])
    def process_bot_message():
        """
        Get stats data from incoming request body (sent by bot) and store it in database
        """

        app.logger.debug('Incoming bot request')

        if request.method == "POST":
            data = request.json
            app.logger.debug('Got data', data)

            return data

    return app


# We need this for test not to run server, only main process will run it
if __name__ == "__main__":
    server_app = create_app()

    server_app.run(host='0.0.0.0', port=7001)
