import datetime as date
from database import stats_represent, add_scores
from parse_message import parse_message
from telegram import Bot, Update, ForceReply
from telegram.ext import Dispatcher, CommandHandler, CallbackContext, MessageHandler, Filters, UpdateFilter


class ScoresMessageFilter(UpdateFilter):
    def filter(self, update):
        return ':' in update.message.text


class ShowKnownStatsMessageFilter(UpdateFilter):
    def filter(self, update):
        # TODO We should make a request to database and check, do we know this activity
        return True


scores_message_filter = ScoresMessageFilter()
show_known_stats_message_filter = ShowKnownStatsMessageFilter()


class StatsBot:
    def __init__(self, token):
        self.bot = Bot(token)
        self.dispatcher = Dispatcher(self.bot, None, workers=0)
        self.dispatcher.add_handler(CommandHandler("add", add_stats_command))
        self.dispatcher.add_handler(CommandHandler("show", show_stats_command))
        self.dispatcher.add_handler(
            MessageHandler(scores_message_filter & ~Filters.command, process_add_stats_message))
        self.dispatcher.add_handler(
            MessageHandler(show_known_stats_message_filter & ~scores_message_filter & ~Filters.command,
                           process_show_stats_message))

    def process_update(self, request):
        update = Update.de_json(request, self.bot)
        print('Update decoded', update.update_id)
        self.dispatcher.process_update(update)
        print('Stats request processed successfully', update.update_id)


def add_stats_command(update, context: CallbackContext):
    update.message.reply_text("Добавить статы (уже есть Червяки, Рэпп, Поводили)",
                              reply_markup=ForceReply(selective=True))


def show_stats_command(update, context: CallbackContext):
    # TODO We should make a request for games to get the list for hint, hardcoding for now
    update.message.reply_text("Показать статы (Червяки, Рэпп, Поводили)", reply_markup=ForceReply(selective=True))


def process_show_stats_message(update, context: CallbackContext):
    data = update.message.text
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


def process_add_stats_message(update: Update, context: CallbackContext):
    data = update.message.text
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
