from telebot.types import BotCommand
from utils.i18n import get_commands_for_lang, TMDB_LANG


def set_default_commands(bot):
    for lang in TMDB_LANG.keys():
        commands = [
            BotCommand(command, description)
            for command, description in get_commands_for_lang(lang)
        ]
        bot.set_my_commands(commands, language_code=lang)
