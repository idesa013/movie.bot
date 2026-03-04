from telebot.types import Message

from loader import bot
from states.director import DirectorSearchState
from utils.i18n import get_user_language


@bot.message_handler(func=lambda m: m.text in ("🎬 Search Director", "🎬 Поиск режиссёра"))
def start_director_search(message: Message):
    lang = get_user_language(message.from_user.id)

    bot.set_state(message.from_user.id, DirectorSearchState.waiting_for_director_name, message.chat.id)

    if lang == "ru":
        bot.send_message(message.chat.id, "Введите имя режиссёра:")
    else:
        bot.send_message(message.chat.id, "Enter the director name:")
