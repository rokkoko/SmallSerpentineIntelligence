import datetime as date
from database import stats_represent, add_scores
from parse_message import parse_message
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext


def is_bot_added_first_time_update(message):
    return 'new_chat_member' in message and message['new_chat_member']['is_bot'] is True and message['new_chat_member'][
        'username'] == 'testKukarebot'


class StatsBot:
    def __init__(self, token):
        self.bot = Bot('1641912008:AAHfo1PWpj4pRPEmazJjIgiAwtHTTgH5pmM')
        self.dispatcher = Dispatcher(self.bot, None, workers=0)
        self.dispatcher.add_handler(CommandHandler("test", test_command))
        self.dispatcher.add_handler(CommandHandler("register", register_command))

    def process_update(self, request):
        update = Update.de_json(request, self.bot)
        print('Update decoded', update.update_id)

        # Types?
        if is_bot_added_first_time_update(request['message']):
            self.bot.send_message(chat_id=update.effective_chat.id, text='Привет! Я бот, который ведет статистику. '
                                                                         'Например, сколько раз вы играли в Червяков '
                                                                         'или сколько отжиманий сделали только что.')

            self.bot.send_message(chat_id=update.effective_chat.id, text='Чтобы я вас узнал, /register')

        self.dispatcher.process_update(update)
        print('Stats request processed successfully', update.update_id)


def test_command(update, context):
    print(update.effective_chat.id)
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def register_command(update: Update, context: CallbackContext):
    telegram_user = context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    print(telegram_user)
