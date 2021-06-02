import datetime as date
from database import stats_represent, add_scores, get_game_names_list, get_game_id
from parse_message import parse_message
from telegram import Bot, Update, ForceReply
from telegram.ext import Dispatcher, CommandHandler, CallbackContext, MessageHandler, Filters, UpdateFilter


class ScoresMessageFilter(UpdateFilter):
    def filter(self, update):
        return ':' in update.message.text


class KnownStatsMessageFilter(UpdateFilter):
    def filter(self, update):
        game = parse_message(update.message.text)
        return True if get_game_id(game) else False


activity_scores_message_filter = ScoresMessageFilter()
known_activity_message_filter = KnownStatsMessageFilter()


class StatsBot:
    def __init__(self, token):
        self.bot = Bot(token)
        self.dispatcher = Dispatcher(self.bot, None, workers=0)
        self.dispatcher.add_handler(CommandHandler("add", add_stats_command))
        self.dispatcher.add_handler(CommandHandler("show", show_stats_command))
        # self.dispatcher.add_handler(
        #     MessageHandler(activity_scores_message_filter & ~Filters.command, process_add_stats_message))
        # self.dispatcher.add_handler(
        #     MessageHandler(known_activity_message_filter & ~activity_scores_message_filter & ~Filters.command,
        #                    process_show_stats_message))
        # self.dispatcher.add_handler(
        #     MessageHandler(~known_activity_message_filter & ~activity_scores_message_filter & ~Filters.command & ~Filters.animation & ~Filters.text,
        #                    process_unknown_message))



        self.dispatcher.add_handler(
            MessageHandler(
                Filters.animation & (~Filters.command) & (~Filters.text), animation_callback
            )
        )

        # self.dispatcher.add_handler(
        #     MessageHandler(
        #         Filters.text & ~known_activity_message_filter & ~activity_scores_message_filter & ~Filters.command, test
        #     )
        # )
        self.dispatcher.add_handler(
            MessageHandler(
                Filters.text & (~Filters.command) & (~Filters.animation), test
            )
        )

    def process_update(self, request):
        update = Update.de_json(request, self.bot)
        print('Update decoded', update.update_id)
        self.dispatcher.process_update(update)
        print('Stats request processed successfully', update.update_id)


def test(update, context):
    update.message.reply_text('ПАРСИНГ СООБЩЕНИЙ РАБОТАЕТ')


def animation_callback(update, context):
    user_name = update.message.from_user.username
    game_name = 'Botyara'
    score_pair = {user_name: 1}
    update.message.reply_text(f"Статы (+1) ботяры '{user_name}' занесены в Метрику")
    result_dict = add_scores(game_name, score_pair)

    result_msg = f'На {date.datetime.today().replace(microsecond=0)} ' \
                 f' БОТЯРЫ имеют следующие статы:\n'
    for user_name, score in result_dict.items():
        result_msg += user_name + ': ' + str(score) + '\n'

    update.message.reply_text(result_msg)


def add_stats_command(update, context):
    update.message.reply_text(
        f'Добавить статы для активности (уже зарегистрированные: {", ".join(get_game_names_list())})',
        reply_markup=ForceReply(selective=True))


def show_stats_command(update, context):
    update.message.reply_text(
        f'Показать статы для активности (уже зарегистрированные: {", ".join(get_game_names_list())})',
        reply_markup=ForceReply(selective=True))


def process_unknown_message(update, context):
    update.message.reply_text('В эту игру вы еще не шпилили')


def process_show_stats_message(update, context):
    data = update.message.text
    game = parse_message(data)
    score_pairs = stats_represent(game)

    if isinstance(score_pairs, dict):
        result_dict = score_pairs

    result_msg = f'На {date.datetime.today().replace(microsecond=0)} ' \
                 f'по игре "{game}" {"общие статы ВСЕХ игрокококов такие"}:\n'
    for user_name, score in result_dict.items():
        result_msg += user_name + ': ' + str(score) + '\n'

    update.message.reply_text(result_msg)


def process_add_stats_message(update: Update, context: CallbackContext):
    data = update.message.text
    game, score_pairs = parse_message(data)
    result_dict = add_scores(game, score_pairs)
    if isinstance(result_dict, str):
        negative_score_msg = result_dict
        update.message.reply_text(negative_score_msg)
        return

    result_msg = f'На {date.datetime.today().replace(microsecond=0)} ' \
                 f'по игре "{game}" {"статы для текущих игрококов"}:\n'
    for user_name, score in result_dict.items():
        result_msg += user_name + ': ' + str(score) + '\n'

    update.message.reply_text(result_msg)
