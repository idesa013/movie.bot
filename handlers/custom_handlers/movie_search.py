from datetime import datetime
from operator import ge
from telebot.types import Message
import requests
from loader import bot
from config_data.config import DATE_FORMAT, TMBD_API_KEY
from states.movie import MovieSearchState
from database.logs import log_movie_search
from html import escape  # для безопасного отображения текста
from database.favorites import remove_favorite  # создадим эту функцию
from keyboards.inline.add_to_fav import add_favorites_button
from database.favorites import check_favorite  # для проверки наличия в избранном


# Временное хранилище данных о фильмах для callback
bot_data = {}


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

    # Подробная информация о фильме (для жанров)
    details = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}",
        params={"api_key": TMBD_API_KEY, "language": "ru-RU"},
    ).json()

    # Жанры
    genres = details.get("genres", [])
    genres_text = ", ".join(f'<b>{g["name"]}</b>' for g in genres) or "n/a"

    # IDs всех жанров через пробел
    genre_ids_str = " ".join(str(g["id"]) for g in genres) if genres else ""

    # Информация о съемочной группе
    credits = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/credits",
        params={"api_key": TMBD_API_KEY, "language": "ru-RU"},
    ).json()

    # Логируем поиск
    log_movie_search(message.from_user.id, movie_id, search_time, genre_ids_str)

    # Режиссёры через запятую с ссылками на Google
    directors_list = [
        f'<a href="https://www.google.com/search?q={escape(d)}+director">{escape(d)}</a>'
        for d in [
            c["name"] for c in credits.get("crew", []) if c.get("job") == "Director"
        ]
    ]
    directors_text = ", ".join(directors_list) if directors_list else "n/a"

    # Формируем текст
    text = (
        f"🎬 {escape(movie.get('title', ''))} (<b>{escape(movie.get('original_title', ''))}</b>)\n"
        f"📅 Release Date: <b>{movie.get('release_date', 'n/a')}</b>\n"
        f"⭐ Raiting: <b>{movie.get('vote_average', 'n/a')}</b>\n"
        f"🎭 Жанры: {genres_text}\n"
        f"🎬 Режиссёры: {directors_text}\n\n"
        f"{escape(movie.get('overview', 'No description available'))}\n\n"
        f"👥 Starring:\n"
    )

    # Актёры с ссылками
    for actor in credits.get("cast", [])[:8]:
        name = escape(actor["name"])
        char = escape(actor["character"])
        google = f"https://www.google.com/search?q={name}+actor"
        text += f'<a href="{google}">{name}</a> — {char}\n'

    # Отправка постера отдельным сообщением, чтобы не превышать лимит
    if movie.get("poster_path"):
        poster = "https://image.tmdb.org/t/p/w500" + movie["poster_path"]
        bot.send_photo(message.chat.id, poster)

    # Текст отдельным сообщением
    # Проверяем, есть ли фильм у пользователя в избранном
    in_favorites = check_favorite(message.from_user.id, movie_id)

    # Сохраняем данные для callback
    bot_data[message.from_user.id] = {
        "movie_id": movie_id,
        "genre_ids": genre_ids_str,
        "movie_name": movie.get("title", "Movie"),
        "search_time": search_time,
    }

    markup = add_favorites_button(movie_id, in_favorites=in_favorites)
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)

    # Очистка состояния
    bot.delete_state(message.from_user.id, message.chat.id)
