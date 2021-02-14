import datetime as date
from database import stats_represent, add_scores
from parse_message import parse_message
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext


class StatsBot:
    def __init__(self, token):
        self.bot = Bot(token)
        self.dispatcher = Dispatcher(self.bot, None, workers=0)
        self.dispatcher.add_handler(CommandHandler("stats", stats_command))

    def process_update(self, request):
        update = Update.de_json(request, self.bot)
        print('Update decoded', update.update_id, update.message.text)
        self.dispatcher.process_update(update)
        print('Stats request processed successfully', update.update_id)


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
            return
        elif isinstance(score_pairs, dict):
            result_dict = score_pairs
            case = 'общие статы ВСЕХ игрокококов такие'
    else:
        result_dict = add_scores(game, score_pairs)
        case = 'статы для текущих игрококов'
        if isinstance(result_dict, str):
            negative_score_msg = result_dict
            update.message.reply_text(negative_score_msg)
            return

    result_msg = f'На {date.datetime.today().replace(microsecond=0)} ' \
                 f'по игре "{game}" {case}:\n'
    for user_name, score in result_dict.items():
        result_msg += user_name + ': ' + str(score) + '\n'

    update.message.reply_text(result_msg)
