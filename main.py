from database.init_db import init_db
from loader import bot
import handlers
from telebot.custom_filters import StateFilter
from utils.set_bot_commands import set_default_commands


def main():
    bot.add_custom_filter(StateFilter(bot))
    set_default_commands(bot)
    init_db()
    bot.infinity_polling()


if __name__ == "__main__":
    main()
