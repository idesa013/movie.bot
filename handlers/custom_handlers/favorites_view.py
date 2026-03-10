import sqlite3
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from loader import bot
from database.db import DB_PATH
from api.tmdb_movie import get_movie_details
from api.tmdb_actor import get_actor_details
from api.tmdb_director import get_director_details
from keyboards.reply.main_menu import _TEXT
from utils.i18n import get_user_language, tmdb_language, ensure_registered


def _title_units(title: str) -> int:
    title = (title or "").strip()
    ln = len(title)
    if ln <= 14:
        return 1
    if ln <= 24:
        return 2
    return 3


def _build_markup(items: list[dict], callback_builder) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    row = []
    used = 0

    def flush():
        nonlocal row, used
        if row:
            markup.row(*row)
            row = []
            used = 0

    for item in items:
        title = item["title"]
        callback_data = callback_builder(item["id"])

        units = _title_units(title)
        btn = InlineKeyboardButton(text=title, callback_data=callback_data, style="primary")

        if units >= 3:
            flush()
            markup.row(btn)
            continue

        if used + units > 3:
            flush()

        row.append(btn)
        used += units

    flush()
    return markup


@bot.message_handler(func=lambda m: (m.text or "").strip() in (_TEXT["en"]["fav_movies"], _TEXT["ru"]["fav_movies"]))
def show_favorite_movies(message: Message):
    if not ensure_registered(bot, message.chat.id, message.from_user.id):
        return

    user_id = message.from_user.id
    lang = get_user_language(user_id)
    tmdb_lang = tmdb_language(lang)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT movie_id
        FROM favorites
        WHERE user_id = ?
        ORDER BY search_time DESC
        """,
        (user_id,),
    )
    movie_ids = [row[0] for row in cur.fetchall()]
    conn.close()

    movies = []
    seen = set()
    for movie_id in movie_ids:
        if movie_id in seen:
            continue
        seen.add(movie_id)
        details = get_movie_details(movie_id, language=tmdb_lang) or {}
        title = details.get("title") or details.get("original_title")
        if title:
            movies.append({"id": movie_id, "title": title})

    if not movies:
        bot.send_message(message.chat.id, "Избранных фильмов нет." if lang == "ru" else "No favorite movies yet.")
        return

    markup = _build_markup(movies, lambda movie_id: f"movie_{movie_id}_movie")
    bot.send_message(message.chat.id, "🎬 Избранные фильмы:" if lang == "ru" else "🎬 Favorite movies:", reply_markup=markup)


@bot.message_handler(func=lambda m: (m.text or "").strip() in (_TEXT["en"]["fav_actors"], _TEXT["ru"]["fav_actors"]))
def show_favorite_actors(message: Message):
    if not ensure_registered(bot, message.chat.id, message.from_user.id):
        return

    user_id = message.from_user.id
    lang = get_user_language(user_id)
    tmdb_lang = tmdb_language(lang)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT actor_id
        FROM actor_favorites
        WHERE user_id = ?
        ORDER BY search_time DESC
        """,
        (user_id,),
    )
    actor_ids = [row[0] for row in cur.fetchall()]
    conn.close()

    actors = []
    seen = set()
    for actor_id in actor_ids:
        if actor_id in seen:
            continue
        seen.add(actor_id)
        details = get_actor_details(actor_id, language=tmdb_lang) or {}
        name = details.get("name")
        if name:
            actors.append({"id": actor_id, "title": name})

    if not actors:
        bot.send_message(message.chat.id, "Избранных актеров нет." if lang == "ru" else "No favorite actors yet.")
        return

    markup = _build_markup(actors, lambda actor_id: f"actor_{actor_id}")
    bot.send_message(message.chat.id, "🎭 Избранные актеры:" if lang == "ru" else "🎭 Favorite actors:", reply_markup=markup)


@bot.message_handler(func=lambda m: (m.text or "").strip() in (_TEXT["en"]["fav_directors"], _TEXT["ru"]["fav_directors"]))
def show_favorite_directors(message: Message):
    if not ensure_registered(bot, message.chat.id, message.from_user.id):
        return

    user_id = message.from_user.id
    lang = get_user_language(user_id)
    tmdb_lang = tmdb_language(lang)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT director_id
        FROM director_favorites
        WHERE user_id = ?
        ORDER BY search_time DESC
        """,
        (user_id,),
    )
    director_ids = [row[0] for row in cur.fetchall()]
    conn.close()

    directors = []
    seen = set()
    for director_id in director_ids:
        if director_id in seen:
            continue
        seen.add(director_id)
        details = get_director_details(director_id, language=tmdb_lang) or {}
        name = details.get("name")
        if name:
            directors.append({"id": director_id, "title": name})

    if not directors:
        bot.send_message(message.chat.id, "Избранных режиссеров нет." if lang == "ru" else "No favorite directors yet.")
        return

    markup = _build_markup(directors, lambda director_id: f"director_{director_id}")
    bot.send_message(message.chat.id, "🎬 Избранные режиссеры:" if lang == "ru" else "🎬 Favorite directors:", reply_markup=markup)