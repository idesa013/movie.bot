from datetime import datetime
from html import escape

from loader import bot
from config_data.config import DATE_FORMAT

from api.tmdb_movie import get_movie_details, get_movie_credits
from database.favorites import check_favorite
from database.logs import log_movie_search

from keyboards.inline.add_to_fav import add_favorites_button
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def send_movie_card(
    chat_id: int,
    movie_id: int,
    user_id: int,
    searched_from: str = "str",
    search_time: str | None = None,
):
    # Подробная информация о фильме
    details = get_movie_details(movie_id) or {}
    credits = get_movie_credits(movie_id) or {}

    # Время для лога
    if not search_time:
        search_time = datetime.now().strftime(DATE_FORMAT)

    # Жанры
    genres = details.get("genres", [])
    genres_text = ", ".join(f"<b>{escape(g['name'])}</b>" for g in genres) or "n/a"
    genre_ids_str = " ".join(str(g["id"]) for g in genres) if genres else ""

    # ✅ Логируем открытие/поиск фильма с источником
    # searched_from: 'str' | 'fav' | 'dir'
    log_movie_search(user_id, movie_id, search_time, genre_ids_str, searched_from=searched_from)

    # Постер (сообщение 1)
    if details.get("poster_path"):
        poster = "https://image.tmdb.org/t/p/w500" + details["poster_path"]
        bot.send_photo(chat_id, poster)

    # Режиссёры (для кнопок)
    directors = [c for c in credits.get("crew", []) if c.get("job") == "Director"]

    # Сообщение 2: краткая инфа + кнопка избранного + кнопки режиссёров
    title = escape(details.get("title", ""))
    original = escape(details.get("original_title", ""))
    info_text = (
        f"🎬 {title} (<b>{original}</b>)\n"
        f"📅 Release Date: <b>{details.get('release_date', 'n/a')}</b>\n"
        f"⭐ Rating: <b>{details.get('vote_average', 'n/a')}</b>\n"
        f"🎭 Жанры: {genres_text}\n"
    )

    # Inline клавиатура: первая строка — избранное; дальше — режиссёры
    in_favorites = check_favorite(user_id, movie_id)
    fav_markup = add_favorites_button(movie_id, in_favorites=in_favorites)

    markup = InlineKeyboardMarkup()
    # строка избранного
    for row in fav_markup.keyboard:
        markup.row(*row)

    # строка(и) режиссёров
    if directors:
        buttons = [
            InlineKeyboardButton(text=d.get("name", "Director"), callback_data=f"director_{d.get('id')}")
            for d in directors
            if d.get("id") is not None
        ]
        # по 2 кнопки в ряд
        for i in range(0, len(buttons), 2):
            markup.row(*buttons[i:i+2])

    bot.send_message(chat_id, info_text, parse_mode="HTML", reply_markup=markup)

    # Сообщение 3: описание + актёры кнопками
    overview = details.get("overview") or "No description available"
    cast = credits.get("cast", [])[:10]

    desc_text = f"{escape(overview)}\n\n👥 Cast:"
    bot.send_message(chat_id, desc_text, parse_mode="HTML", reply_markup=_actors_markup(cast))


def _actors_markup(actors: list):
    from keyboards.inline.movie_actors import movie_actors_markup
    return movie_actors_markup(actors)
