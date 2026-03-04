from telebot.types import Message

from loader import bot
from states.movie import MovieSearchState
from utils.i18n import get_user_language


@bot.message_handler(func=lambda m: m.text in ("🎬 Movie Search", "🎬 Поиск фильма"))
def start_movie_search(message: Message):
    lang = get_user_language(message.from_user.id)

    bot.set_state(message.from_user.id, MovieSearchState.waiting_for_title, message.chat.id)

    if lang == "ru":
        bot.send_message(message.chat.id, "Введите название фильма:")
    else:
        bot.send_message(message.chat.id, "Enter the movie title:")
