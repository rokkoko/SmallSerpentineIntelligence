from flask import Flask
from flask import request
import os
from dotenv import load_dotenv

from stats_bot import StatsBot

load_dotenv()

stats_bot_token = os.getenv("STATS_BOT_TOKEN")


def create_app():
    app = Flask('stats')
    stats_bot = StatsBot(stats_bot_token)

    @app.route('/webhooks/stats/' + stats_bot_token, methods=['POST'])
    def stats_webhook():
        print('Stats webhook request received')
        stats_bot.process_update(request.get_json(force=True))

        return 'ok', 200

    print('App initialized successfully, waiting for requests')

    return app


# We need this for test not to run server, only main process will run it
if __name__ == "__main__":
    server_app = create_app()

    server_app.run(host='0.0.0.0', port=80)
