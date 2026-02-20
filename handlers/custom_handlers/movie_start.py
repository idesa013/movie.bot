from telebot.types import Message
from loader import bot
from states.movie import MovieSearchState


@bot.message_handler(func=lambda m: m.text == "🎬 Movie Search")
def start_movie_search(message: Message):
    bot.set_state(
        message.from_user.id, MovieSearchState.waiting_for_title, message.chat.id
    )
    bot.send_message(message.chat.id, "Enter the movie title:")
