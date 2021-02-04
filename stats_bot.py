import logging
from dotenv import load_dotenv
import os
import datetime as date

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Use environment variables from .env file
from database import stats_represent, add_scores
from parse_message import parse_message

load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def stats_command(update: Update, context: CallbackContext) -> None:
    data = ' '.join(context.args)
    try:
        game, score_pairs = parse_message(data)
    except (ValueError, TypeError):
        game = parse_message(data)
        score_pairs = stats_represent(game)
        if isinstance(score_pairs, str):
            no_such_game_msg = score_pairs
            update.message.reply_text(no_such_game_msg)
            case = None
            result_dict = None
        elif isinstance(score_pairs, dict):
            result_dict = score_pairs
            case = 'общие статы ВСЕХ игрокококов такие'
    else:
        result_dict = add_scores(game, score_pairs)
        case = 'статы для текущих игрококов'
        if isinstance(result_dict, str):
            negative_score_msg = result_dict
            update.message.reply_text(negative_score_msg)

    result_msg = f'На {date.datetime.today().replace(microsecond=0)} ' \
                 f'по игре "{game}" {case}:\n'
    for user_name, score in result_dict.items():
        result_msg += user_name + ': ' + str(score) + '\n'

    update.message.reply_text(result_msg)


if __name__ == '__main__':
    token = os.getenv("STATS_BOT_TOKEN")
    port = int(os.environ.get('PORT', '8443'))

    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("stats", stats_command))

    # updater.start_polling()

    updater.start_webhook(listen="0.0.0.0",
                          port=port,
                          url_path=token)

    updater.bot.set_webhook("https://kokostats.herokuapp.com/" + token)

    updater.idle()
