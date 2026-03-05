from datetime import datetime
from html import escape

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import bot
from config_data.config import DATE_FORMAT

from api.tmdb_movie import get_movie_details, get_movie_credits
from database.favorites import check_favorite
from database.logs import log_movie_search
from keyboards.inline.add_to_fav import add_favorites_button


CAPTION_LIMIT = 1024  # Telegram caption limit for send_photo


def _chunked(items, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _build_movie_markup(
    user_id: int, movie_id: int, credits: dict
) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()

    # 1) Режиссёры — до 3 кнопок в ряд
    directors = []
    seen_dir = set()
    for c in credits.get("crew", []) or []:
        if c.get("job") != "Director":
            continue
        dir_id = c.get("id")
        name = c.get("name")
        if dir_id is None or not name:
            continue
        if dir_id in seen_dir:
            continue
        seen_dir.add(dir_id)
        directors.append((dir_id, name))

    director_buttons = [
        InlineKeyboardButton(text=name, callback_data=f"director_{dir_id}")
        for dir_id, name in directors
    ]
    for row in _chunked(director_buttons, 3):
        markup.row(*row)

    # 2) Актёры — до 3 кнопок в ряд + style="primary"
    actors = []
    seen_act = set()
    for a in (credits.get("cast", []) or [])[:15]:
        act_id = a.get("id")
        name = a.get("name")
        if act_id is None or not name:
            continue
        if act_id in seen_act:
            continue
        seen_act.add(act_id)
        actors.append((act_id, name))

    actor_buttons = [
        InlineKeyboardButton(
            text=name, callback_data=f"actor_{act_id}", style="primary"
        )
        for act_id, name in actors
    ]
    for row in _chunked(actor_buttons, 3):
        markup.row(*row)

    # 3) Избранное — последней строкой
    in_favorites = check_favorite(user_id, movie_id)
    fav_markup = add_favorites_button(movie_id, in_favorites=in_favorites)
    for row in fav_markup.keyboard:
        markup.row(*row)

    return markup


def _send_photo_or_fallback(
    chat_id: int, poster_url: str, text: str, markup: InlineKeyboardMarkup
):
    """
    Если caption слишком длинный — Telegram вернёт 400 (caption is too long).
    Тогда отправляем:
      1) фото без caption
      2) отдельное сообщение с текстом + кнопками
    """
    if len(text) <= CAPTION_LIMIT:
        bot.send_photo(
            chat_id, poster_url, caption=text, parse_mode="HTML", reply_markup=markup
        )
        return

    bot.send_photo(chat_id, poster_url)
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)


def send_movie_card(
    chat_id: int,
    movie_id: int,
    user_id: int,
    searched_from: str = "str",
    search_time: str | None = None,
):
    details = get_movie_details(movie_id) or {}
    credits = get_movie_credits(movie_id) or {}

    if not search_time:
        search_time = datetime.now().strftime(DATE_FORMAT)

    # жанры + ids для логов
    genres = details.get("genres", []) or []
    genres_text = (
        ", ".join(escape(g.get("name", "")) for g in genres if g.get("name")) or "n/a"
    )
    genre_ids_str = (
        " ".join(str(g["id"]) for g in genres if g.get("id") is not None)
        if genres
        else ""
    )

    # логирование
    log_movie_search(
        user_id, movie_id, search_time, genre_ids_str, searched_from=searched_from
    )

    title = escape(details.get("title", ""))
    original = escape(details.get("original_title", ""))
    release_date = escape(details.get("release_date", "n/a"))
    rating = details.get("vote_average", "n/a")

    # описание
    overview_raw = details.get("overview") or "No description available"
    overview = escape(overview_raw)

    text = (
        f"🎬 <b>{title}</b>"
        + (f" (<b>{original}</b>)" if original and original != title else "")
        + "\n"
        f"📅 Release Date: <b>{release_date}</b>\n"
        f"⭐ Rating: <b>{rating}</b>\n"
        f"🎭 Жанры: <b>{genres_text}</b>\n\n"
        f"<blockquote expandable>{overview}</blockquote>\n\n"
        f"🎬 <b>Режиссёры:</b> / <code>👥 <b>Актёры:</b></code>"
    )

    markup = _build_movie_markup(user_id=user_id, movie_id=movie_id, credits=credits)

    if details.get("poster_path"):
        poster = "https://image.tmdb.org/t/p/w500" + details["poster_path"]
        _send_photo_or_fallback(chat_id, poster, text, markup)
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
