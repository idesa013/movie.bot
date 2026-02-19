from telebot.types import Message
import requests
from config_data.config import TMBD_API_KEY
from loader import bot


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
# @bot.message_handler(state=None)
# def bot_echo(message: Message):
#     bot.reply_to( message, "Эхо без состояния или фильтра.\n" f"Сообщение: {message.text}")


@bot.message_handler(func=lambda m: True)
def search_movie(message):
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
    title = movie.get("title")
    orig_title = movie.get("original_title")
    date = movie.get("release_date")
    rating = movie.get("vote_average")
    overview = movie.get("overview")

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
    params = {"api_key": TMBD_API_KEY, "language": "ru-RU"}

    data = requests.get(url, params=params).json()

    text = (
        f"🎬 {title} (<b>{orig_title}</b>)\n"
        f"📅 {date}\n"
        f"⭐ {rating}\n\n"
        f"{overview}\n\n"
        f"👥 В главных ролях:\n"
    )
    for actor in data["cast"][:10]:
        name = actor["name"]
        google_url = f"https://www.google.com/search?q={name}+actor"
        text += f'<a href="{google_url}">{name}</a> —> {actor['character']}\n'

    # постер
    if movie.get("poster_path"):
        poster = "https://image.tmdb.org/t/p/w500" + movie["poster_path"]
        bot.send_photo(message.chat.id, poster, caption=text, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, text)
