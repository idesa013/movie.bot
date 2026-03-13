import re
import sqlite3
from collections import Counter
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from loader import bot
from states.movie import MovieSearchState
from utils.i18n import get_user_language, tmdb_language, t, ensure_registered
from api.tmdb_movie import discover_movies_by_genre, discover_new_movies
from utils.access import ensure_user_not_blocked
from database.db import DB_PATH
from keyboards.reply.main_menu import _TEXT


GENRE_NAMES = {
    28: {"en": "Action", "ru": "Боевик"},
    12: {"en": "Adventure", "ru": "Приключения"},
    16: {"en": "Animation", "ru": "Мультфильм"},
    35: {"en": "Comedy", "ru": "Комедия"},
    80: {"en": "Crime", "ru": "Криминал"},
    99: {"en": "Documentary", "ru": "Документальный"},
    18: {"en": "Drama", "ru": "Драма"},
    10751: {"en": "Family", "ru": "Семейный"},
    14: {"en": "Fantasy", "ru": "Фэнтези"},
    36: {"en": "History", "ru": "История"},
    27: {"en": "Horror", "ru": "Ужасы"},
    10402: {"en": "Music", "ru": "Музыка"},
    9648: {"en": "Mystery", "ru": "Детектив"},
    10749: {"en": "Romance", "ru": "Мелодрама"},
    878: {"en": "Science Fiction", "ru": "Фантастика"},
    10770: {"en": "TV Movie", "ru": "Телефильм"},
    53: {"en": "Thriller", "ru": "Триллер"},
    10752: {"en": "War", "ru": "Военный"},
    37: {"en": "Western", "ru": "Вестерн"},
}


def _title_units(title: str) -> int:
    ttitle = (title or "").strip()
    ln = len(ttitle)
    if ln <= 14:
        return 1
    if ln <= 24:
        return 2
    return 3


def _movie_markup(movies: list[dict]) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()

    row = []
    used = 0

    def flush():
        nonlocal row, used
        if row:
            markup.row(*row)
            row = []
            used = 0

    for movie in movies:
        title = (movie.get("title") or movie.get("original_title") or "Movie").strip()
        movie_id = movie.get("id")
        if not movie_id:
            continue

        units = _title_units(title)
        btn = InlineKeyboardButton(
            text=title,
            callback_data=f"movie_recom:{movie_id}",
            style="primary",
        )

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


def _favorite_genre_id(user_id: int) -> int | None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT genre_ids
        FROM favorites
        WHERE user_id = ?
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()

    genre_counter = Counter()

    for (genre_ids_str,) in rows:
        if not genre_ids_str:
            continue

        parts = [p for p in re.split(r"[\s,]+", genre_ids_str.strip()) if p]
        for part in parts:
            if part.isdigit():
                genre_counter[int(part)] += 1

    if not genre_counter:
        return None

    return genre_counter.most_common(1)[0][0]


def _favorite_movie_ids(user_id: int) -> set[int]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT movie_id FROM favorites WHERE user_id = ?", (user_id,))
    ids = {row[0] for row in cur.fetchall()}
    conn.close()
    return ids


def _genre_name(genre_id: int, lang: str) -> str:
    pack = GENRE_NAMES.get(genre_id)
    if not pack:
        return str(genre_id)
    return pack.get(lang, pack["en"])


def _collect_movies(fetch_page, favorite_ids: set[int], limit: int = 12) -> list[dict]:
    movies = []
    seen_ids = set()

    for page in range(1, 6):
        data = fetch_page(page)
        results = data.get("results") or []

        for movie in results:
            mid = movie.get("id")
            if not mid or mid in favorite_ids or mid in seen_ids:
                continue
            seen_ids.add(mid)
            movies.append(movie)
            if len(movies) >= limit:
                return movies

    return movies


@bot.message_handler(
    func=lambda m: m.text in (_TEXT["en"]["movie"], _TEXT["ru"]["movie"])
)
def start_movie_search(message: Message):
    if not ensure_user_not_blocked(bot, message.chat.id, message.from_user.id):
        return

    if not ensure_registered(bot, message.chat.id, message.from_user.id):
        return

    lang = get_user_language(message.from_user.id)
    bot.set_state(
        message.from_user.id, MovieSearchState.waiting_for_title, message.chat.id
    )
    bot.send_message(message.chat.id, t(lang, "enter_movie_title"))


@bot.message_handler(
    func=lambda m: m.text in (_TEXT["en"]["rec_new"], _TEXT["ru"]["rec_new"])
)
def show_new_recommendations(message: Message):
    if not ensure_user_not_blocked(bot, message.chat.id, message.from_user.id):
        return

    if not ensure_registered(bot, message.chat.id, message.from_user.id):
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    lang = get_user_language(user_id)
    tmdb_lang = tmdb_language(lang)
    favorite_ids = _favorite_movie_ids(user_id)

    movies = _collect_movies(
        lambda page: discover_new_movies(
            language=tmdb_lang, page=page, vote_average_gte=4
        ),
        favorite_ids,
        limit=12,
    )

    if not movies:
        bot.send_message(chat_id, t(lang, "recommendations_empty"))
        return

    markup = _movie_markup(movies)
    bot.send_message(chat_id, t(lang, "new_releases_title"), reply_markup=markup)


@bot.message_handler(
    func=lambda m: m.text in (_TEXT["en"]["rec_genre"], _TEXT["ru"]["rec_genre"])
)
def show_recommendations(message: Message):
    if not ensure_user_not_blocked(bot, message.chat.id, message.from_user.id):
        return

    if not ensure_registered(bot, message.chat.id, message.from_user.id):
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    lang = get_user_language(user_id)
    tmdb_lang = tmdb_language(lang)

    genre_id = _favorite_genre_id(user_id)
    if genre_id is None:
        bot.send_message(chat_id, t(lang, "recommendations_empty"))
        return

    favorite_ids = _favorite_movie_ids(user_id)

    movies = _collect_movies(
        lambda page: discover_movies_by_genre(
            genre_id,
            language=tmdb_lang,
            page=page,
            sort_by="popularity.desc",
            vote_average_gte=4,
        ),
        favorite_ids,
        limit=12,
    )

    if not movies:
        bot.send_message(chat_id, t(lang, "recommendations_empty"))
        return

    genre_name = _genre_name(genre_id, lang)
    bot.send_message(
        chat_id,
        t(lang, "recommendations_by_genre_title", genre_name=genre_name),
        parse_mode="HTML",
        reply_markup=_movie_markup(movies),
    )


@bot.message_handler(
    func=lambda m: m.text
    in (_TEXT["en"]["rec_new_genre"], _TEXT["ru"]["rec_new_genre"])
)
def show_new_genre_recommendations(message: Message):
    if not ensure_user_not_blocked(bot, message.chat.id, message.from_user.id):
        return

    if not ensure_registered(bot, message.chat.id, message.from_user.id):
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    lang = get_user_language(user_id)
    tmdb_lang = tmdb_language(lang)

    genre_id = _favorite_genre_id(user_id)
    if genre_id is None:
        bot.send_message(chat_id, t(lang, "recommendations_empty"))
        return

    favorite_ids = _favorite_movie_ids(user_id)

    movies = _collect_movies(
        lambda page: discover_movies_by_genre(
            genre_id,
            language=tmdb_lang,
            page=page,
            sort_by="primary_release_date.desc",
            vote_average_gte=4,
        ),
        favorite_ids,
        limit=12,
    )

    if not movies:
        bot.send_message(chat_id, t(lang, "recommendations_empty"))
        return

    genre_name = _genre_name(genre_id, lang)
    bot.send_message(
        chat_id,
        t(lang, "new_by_genre_title", genre_name=genre_name),
        parse_mode="HTML",
        reply_markup=_movie_markup(movies),
    )
