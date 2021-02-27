import datetime as date
from database import stats_represent, add_scores
from parse_message import parse_message
from telegram import Bot, Update, InlineQueryResultArticle, InputTextMessageContent, ParseMode, InlineKeyboardButton, \
    InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackContext, InlineQueryHandler, CallbackQueryHandler, \
    MessageHandler, Filters, ConversationHandler

from telegram.utils.helpers import escape_markdown


def is_registered_user(update):
    return False


def cancel(update: Update, context: CallbackContext):
    return ConversationHandler.END


class StatsBot:
    def __init__(self, token):
        self.bot = Bot('1641912008:AAHfo1PWpj4pRPEmazJjIgiAwtHTTgH5pmM')
        self.dispatcher = Dispatcher(self.bot, None, workers=0)
        # self.dispatcher.add_handler(CommandHandler("stats", test_command))j
        # self.dispatcher.add_handler(CommandHandler("start", start_command))
        self.dispatcher.add_handler(InlineQueryHandler(inline_query))
        # self.dispatcher.add_handler(CallbackQueryHandler(button))

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start_command)],
            states={
                1: [MessageHandler(Filters.text & ~Filters.command, nickname)],
                2: [MessageHandler(Filters.text & ~Filters.command, practice)],
                3: [MessageHandler(Filters.text & ~Filters.command, practice2)]
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        self.dispatcher.add_handler(conv_handler)

    def process_update(self, request):
        update = Update.de_json(request, self.bot)
        print('Update decoded', update.update_id)
        self.dispatcher.process_update(update)


def inline_query(update, context):
    print('Fired')
    if is_registered_user(update):
        query = update.inline_query.query
        results = [
            InlineQueryResultArticle(
                id="sdkjfkldsfkl", title=query, input_message_content=InputTextMessageContent(query)
            )
        ]
        update.inline_query.answer([], switch_pm_text='Register', switch_pm_parameter='register')
    else:
        update.inline_query.answer([], switch_pm_text='Register', switch_pm_parameter='register')


def test_command(update, context):
    print(update)


def start_command(update, context):
    update.message.reply_text(
        'Привет! Я бот для учета статистики, например, отжиманий или количество выпитого пива. '
        'Бот сохраняет статистику на сервер, поэтому вам нужно зарегистрироваться.',
    )

    update.message.reply_text(
        'Какое имя использовать в списках статистики?',
    )

    return 1

    # keyboard = [
    #     InlineKeyboardButton("Option 1", switch_inline_query='register'),
    # ]
    #
    # reply_markup = InlineKeyboardMarkup(keyboard)
    #
    # update.message.reply_text('Please choose:', reply_markup=reply_markup)
    # if 'register' in context.args:
    #     context.bot.send_message(chat_id=update.effective_chat.id, text="Start with parameter")
    # else:
    #     context.bot.send_message(chat_id=update.effective_chat.id, text="Random start")


def button(update: Update, context: CallbackContext) -> None:
    pass
    # query = update.callback_query
    #
    # # CallbackQueries need to be answered, even if no notification to the user is needed
    # # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    # query.answer()
    #
    # query.edit_message_text(text=f"Selected option: {query.data}")


def nickname(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user

    print("Bio of %s: %s", user.first_name, update.message.text)
    context.user_data['user'] = user
    context.user_data['nickname'] = update.message.text

    update.message.reply_text(
        "Спасибо, ваша статистика будет под именем <strong>{}</strong>. "
        "Чтобы записать метрику, используйте команду <code>/add</code>. "
        "Попробуйте сейчас - напишите <code>/add Яблоко 1</code>".format(
            update.message.text),
        parse_mode=ParseMode.HTML)

    return 2


def practice(update, context):
    user = update.message.from_user
    update.message.reply_text(
        "Команда <code>/add</code> добавляет метрику, <code>Яблоко</code> это название метрики, а <code>1</code> сколько добавить к метрике.",
        parse_mode=ParseMode.HTML)
    update.message.reply_text("Чтобы посмотреть текущее количество яблок, напишите <code>/show Яблоко</code>.",
                              parse_mode=ParseMode.HTML)

    return 3


def practice2(update, context):
    keyboard = [
        [InlineKeyboardButton("Open rokkoko.heroku.com", url="google.com")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    user = update.message.from_user

    print(context.user_data)
    update.message.reply_text(
        "Бот готов к использованию. Данные хранятся на сайте rokkoko.heroku.com, и вы всегда можете и"
        " посмотреть. Для этого по ссылке, чтобы создать аккаунт и завершить регистрацию. Спасибо.",
        reply_markup=reply_markup)
