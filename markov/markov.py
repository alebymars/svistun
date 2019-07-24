import telebot
import logging
import functools
from markov import speech
from markov.settings import settings
from markov.filters import message_filter

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(settings.TELEGRAM_TOKEN)


def admin_required(func):
    @functools.wraps(func)
    def wrapper_admin_required(message, *args, **kwargs):
        username = message.from_user.username
        chat_id = str(message.chat.id)
        username_admins = []
        if message.chat.type != 'private':
            username_admins = [
                u.user.username for u in bot.get_chat_administrators(chat_id)
            ]
        if username in username_admins + settings.ADMIN_USERNAMES:
            return func(message, *args, **kwargs)
        else:
            bot.reply_to(message, 'Функция доступна только для администраторов 🤔')
    return wrapper_admin_required


def confirmation_required(func):
    @functools.wraps(func)
    def wrapper_confirmation_required(message, *args, **kwargs):
        if message.text.startswith('/'):
            markup = telebot.types.ReplyKeyboardMarkup(
                row_width=2, one_time_keyboard=True, selective=True
            )
            markup.add('Да', 'Нет')
            reply = bot.reply_to(
                message, 'уверены ли вы?',
                reply_markup=markup
            )
            logger.info(f'отправка подтверждения клавиатуры на {func.__name__}')
            callback = globals()[func.__name__]
            bot.register_next_step_handler(reply, callback)
            return

        elif message.text == 'Да':
            logger.info(f'получено положительное подтверждение для {func.__name__}')
            func(message, *args, **kwargs)

        logger.info('удаление клавиатуры')
        markup = telebot.types.ReplyKeyboardRemove()
        bot.reply_to(message, 'Отлично', reply_markup=markup)

    return wrapper_confirmation_required


@bot.message_handler(commands=[settings.SENTENCE_COMMAND])
def generate_sentence(message, reply=False):
    logger.info(f'предложение CMD вызывается в чате {message.chat.id}')
    generated_message = speech.new_message(message.chat)
    if reply:
        bot.reply_to(message, generated_message)
    else:
        bot.send_message(message.chat.id, generated_message)


@bot.message_handler(commands=[settings.REMOVE_COMMAND])
@admin_required
@confirmation_required
def remove_messages(message):
    logger.info(f'удалить cmd вызывается в чате {message.chat.id}')
    speech.delete_model(message.chat)


@bot.message_handler(commands=[settings.VERSION_COMMAND])
def get_repo_version(message):
    logger.info(f'версия cmd вызывается из чата {message.chat.id}')
    hash_len = 7
    commit_hash = settings.COMMIT_HASH[:hash_len]
    bot.reply_to(message, commit_hash)


@bot.message_handler(commands=[settings.FLUSH_COMMAND])
@admin_required
@confirmation_required
def flush_cache(message):
    logger.info(f'flush cmd вызывается в чате {message.chat.id}')
    speech.flush()


@bot.message_handler(commands=[settings.HELP_COMMAND])
def help(message):
    logger.info(f'помощь cmd вызывается в чате {message.chat.id}')
    username = bot.get_me().username
    sentence_command = settings.SENTENCE_COMMAND
    remove_command = settings.REMOVE_COMMAND
    version_command = settings.VERSION_COMMAND
    flush_command = settings.FLUSH_COMMAND
    start_command = settings.START_COMMAND
    help_command = settings.HELP_COMMAND

    help_text = (
        "Добро пожаловать в DeniskaBot, бот Telegram, который пишет "
        "рандомный текст, сделан на Markov chains!\n\n"
        "/{sentence_command}: {username} сгенерировать сообщение.\n"
        "/{remove_command}: {username} удалить сообщения из чата.\n"
        "/{version_command}: {username} текущая версия.\n"
        "/{flush_command}: {username} почистить кэш.\n"
        "/{help_command}: {username} помощь!"
    )
    output_text = help_text.format(
        username=username, sentence_command=sentence_command,
        remove_command=remove_command, version_command=version_command,
        flush_command=flush_command, start_command=start_command,
        help_command=help_command
    )
    bot.reply_to(message, output_text)


@bot.message_handler(commands=[settings.START_COMMAND])
def start(message):
    bot.reply_to(message, f"Добро пожаловать в DeniskaBot, бот Telegram, который пишет "
                          f"интересные штуки, запустить /{settings.SENTENCE_COMMAND} "
                          f"Для получения дополнительной информации используйте "
                          f"/{settings.HELP_COMMAND}.")


@bot.message_handler(func=message_filter)
def handle_message(message):
    try:
        speech.update_model(message.chat, message.text)
    except ValueError as er:
        logger.error(er)
        return
    if f'@{bot.get_me().username}' in message.text:
        generate_sentence(message, reply=True)


def notify_admin(message):
    if settings.ADMIN_CHAT_ID and message:
        bot.send_message(settings.ADMIN_CHAT_ID, message)
    logger.info(message)


if __name__ == '__main__':
    notify_admin('бот стартанул')
    bot.polling(none_stop=True)
