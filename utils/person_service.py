from datetime import datetime
from html import escape

from loader import bot
from config_data.config import DATE_FORMAT

from api.tmdb_actor import get_actor_details, get_actor_movie_credits
from api.tmdb_director import get_director_details, get_director_movie_credits

from database.logs import log_actor_search, log_director_search
from database.actor_favorites import check_actor_favorite
from database.director_favorites import check_director_favorite

from keyboards.inline.add_to_actor_fav import add_actor_favorites_button
from keyboards.inline.add_to_director_fav import add_director_favorites_button

from keyboards.inline.actor_movies import actor_movies_markup
from keyboards.inline.director_movies import director_movies_markup


def _sorted_movies_no_docs(movies: list, limit: int = 10) -> list:
    # исключаем документальные (genre id 99)
    filtered = [m for m in movies if 99 not in m.get("genre_ids", [])]
    return sorted(filtered, key=lambda m: m.get("popularity", 0), reverse=True)[:limit]


def send_actor_card(chat_id: int, user_id: int, actor_id: int, searched_from: str = "str"):
    details = get_actor_details(actor_id) or {}
    credits = get_actor_movie_credits(actor_id) or {}

    search_time = datetime.now().strftime(DATE_FORMAT)
    log_actor_search(user_id, actor_id, search_time, searched_from=searched_from)

    text = (
        f"🎭 <b>{escape(details.get('name', ''))}</b>\n"
        f"📅 Birthday: <b>{details.get('birthday', 'n/a')}</b>\n"
        f"🌍 Place of birth: <b>{escape(details.get('place_of_birth', 'n/a'))}</b>\n\n"
    )

    biography = details.get("biography") or "No biography available"
    text += f"<blockquote expandable>{escape(biography)}</blockquote>\n\n"
    text += "🎬 Known for:\n"

    known_movies = _sorted_movies_no_docs(credits.get("cast", []), limit=10)

    # Фото
    if details.get("profile_path"):
        photo = "https://image.tmdb.org/t/p/w500" + details["profile_path"]
        bot.send_photo(chat_id, photo)

    # Избранное актёра
    in_favorites = check_actor_favorite(user_id, actor_id)
    fav_markup = add_actor_favorites_button(actor_id, in_favorites=in_favorites)

    # Кнопки фильмов
    movies_markup = actor_movies_markup(known_movies)

    # Отправляем: (1) текст + кнопка избранного, (2) фильмы
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=fav_markup)
    bot.send_message(chat_id, "Select a movie:", reply_markup=movies_markup)


def send_director_card(chat_id: int, user_id: int, director_id: int, searched_from: str = "str"):
    details = get_director_details(director_id) or {}
    credits = get_director_movie_credits(director_id) or {}

    search_time = datetime.now().strftime(DATE_FORMAT)
    log_director_search(user_id, director_id, search_time, searched_from=searched_from)

    text = (
        f"🎬 <b>{escape(details.get('name', ''))}</b>\n"
        f"📅 Birthday: <b>{details.get('birthday', 'n/a')}</b>\n"
        f"🌍 Place of birth: <b>{escape(details.get('place_of_birth', 'n/a'))}</b>\n\n"
    )

    biography = details.get("biography") or "No biography available"
    text += f"<blockquote expandable>{escape(biography)}</blockquote>\n\n"
    text += "🎬 Directed:\n"

    # В movie_credits режиссёрские работы лежат в crew (job == Director)
    crew = credits.get("crew", [])
    directed = [m for m in crew if m.get("job") == "Director"]
    known_movies = _sorted_movies_no_docs(directed, limit=10)

    if details.get("profile_path"):
        photo = "https://image.tmdb.org/t/p/w500" + details["profile_path"]
        bot.send_photo(chat_id, photo)

    in_favorites = check_director_favorite(user_id, director_id)
    fav_markup = add_director_favorites_button(director_id, in_favorites=in_favorites)

    movies_markup = director_movies_markup(known_movies)

    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=fav_markup)
    bot.send_message(chat_id, "Select a movie:", reply_markup=movies_markup)
