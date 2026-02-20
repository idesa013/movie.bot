from datetime import datetime
from telebot.types import Message
import requests
from loader import bot
from config_data.config import DATE_FORMAT, TMBD_API_KEY
from states.movie import MovieSearchState
from database.logs import log_movie_search


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
        bot.send_message(message.chat.id, "Фильм не найден")
        return

    movie = results[0]
    movie_id = movie.get("id")
    search_time = datetime.fromtimestamp(message.date).strftime(DATE_FORMAT)

    log_movie_search(message.from_user.id, movie_id, search_time)

    credits = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/credits",
        params={"api_key": TMBD_API_KEY, "language": "ru-RU"},
    ).json()

    text = (
        f"🎬 {movie.get('title')} (<b>{movie.get('original_title')}</b>)\n"
        f"📅 {movie.get('release_date')}\n"
        f"⭐ {movie.get('vote_average')}\n\n"
        f"{movie.get('overview')}\n\n"
        f"👥 В главных ролях:\n"
    )

    for actor in credits["cast"][:8]:
        name = actor["name"]
        char = actor["character"]
        google = f"https://www.google.com/search?q={name}+actor"
        text += f'<a href="{google}">{name}</a> — {char}\n'

    if movie.get("poster_path"):
        poster = "https://image.tmdb.org/t/p/w500" + movie["poster_path"]
        bot.send_photo(message.chat.id, poster, caption=text, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, text, parse_mode="HTML")

    bot.delete_state(message.from_user.id, message.chat.id)
