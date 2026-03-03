from datetime import datetime
from telebot.types import Message
import requests
from loader import bot
from config_data.config import DATE_FORMAT, TMBD_API_KEY
from states.movie import MovieSearchState
from utils.movie_service import send_movie_card


@bot.message_handler(state=MovieSearchState.waiting_for_title)
def search_movie(message: Message):
    query = message.text

    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMBD_API_KEY,
        "query": query,
        "language": "ru-RU",
    }

    r = requests.get(url, params=params).json()
    results = r.get("results")

    if not results:
        bot.send_message(message.chat.id, "Movie not found")
        return

    movie = results[0]
    movie_id = movie.get("id")

    search_time = datetime.fromtimestamp(message.date).strftime(DATE_FORMAT)

    send_movie_card(
        message.chat.id,
        movie_id,
        message.from_user.id,
        searched_from="str",
        search_time=search_time,
    )

    bot.delete_state(message.from_user.id, message.chat.id)
