from telebot.types import BotCommand, BotCommandScopeChat

from utils.i18n import get_commands_for_lang, LANG_EN


def set_default_commands(bot):
    commands = [
        BotCommand(command, description)
        for command, description in get_commands_for_lang(LANG_EN)
    ]
    bot.set_my_commands(commands)


def set_chat_commands(bot, chat_id: int, lang: str):
    commands = [
        BotCommand(command, description)
        for command, description in get_commands_for_lang(lang)
    ]
    bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id))
