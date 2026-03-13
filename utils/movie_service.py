from datetime import datetime
from html import escape

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import bot
from config_data.config import DATE_FORMAT

from api.tmdb_movie import get_movie_details, get_movie_credits
from database.favorites import check_favorite
from database.logs import log_movie_search
from keyboards.inline.add_to_fav import add_favorites_button
from utils.admin_context import has_selected_user, get_selected_user, get_selected_page
from utils.i18n import get_user_language, tmdb_language


CAPTION_LIMIT = 1024


def _chunked(items, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _build_movie_markup(
    user_id: int,
    movie_id: int,
    credits: dict,
    viewer_id: int | None = None,
    lang: str = "en",
) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()

    directors = []
    seen_dir = set()
    for c in credits.get("crew", []) or []:
        if c.get("job") != "Director":
            continue
        dir_id = c.get("id")
        name = c.get("name")
        if dir_id is None or not name or dir_id in seen_dir:
            continue
        seen_dir.add(dir_id)
        directors.append((dir_id, name))

    director_buttons = [
        InlineKeyboardButton(text=name, callback_data=f"director_{dir_id}")
        for dir_id, name in directors
    ]
    for row in _chunked(director_buttons, 3):
        markup.row(*row)

    actors = []
    seen_act = set()
    for a in (credits.get("cast", []) or [])[:15]:
        act_id = a.get("id")
        name = a.get("name")
        if act_id is None or not name or act_id in seen_act:
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

    in_favorites = check_favorite(user_id, movie_id)
    fav_markup = add_favorites_button(movie_id, in_favorites=in_favorites, lang=lang)
    for row in fav_markup.keyboard:
        markup.row(*row)

    if viewer_id is not None and has_selected_user(viewer_id):
        back_text = "⬅ Back to User" if lang == "en" else "⬅ Назад к пользователю"
        markup.row(
            InlineKeyboardButton(
                text=back_text,
                callback_data=f"admin_user_back_to_card:{get_selected_user(viewer_id)}:{get_selected_page(viewer_id)}",
            )
        )

    return markup


def _send_photo_or_fallback(
    chat_id: int, poster_url: str, text: str, markup: InlineKeyboardMarkup
):
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
    viewer_id: int | None = None,
):
    lang = get_user_language(user_id)
    tmdb_lang = tmdb_language(lang)

    details = get_movie_details(movie_id, language=tmdb_lang) or {}
    credits = get_movie_credits(movie_id, language=tmdb_lang) or {}

    if not search_time:
        search_time = datetime.now().strftime(DATE_FORMAT)

    genres = details.get("genres", []) or []
    genres_text = ", ".join(
        escape(g.get("name", "")) for g in genres if g.get("name")
    ) or ("n/a" if lang == "en" else "н/д")
    genre_ids_str = (
        " ".join(str(g["id"]) for g in genres if g.get("id") is not None)
        if genres
        else ""
    )

    log_movie_search(
        user_id, movie_id, search_time, genre_ids_str, searched_from=searched_from
    )

    title = escape(details.get("title", ""))
    original = escape(details.get("original_title", ""))
    release_date = escape(details.get("release_date", "n/a" if lang == "en" else "н/д"))
    rating = details.get("vote_average", "n/a" if lang == "en" else "н/д")

    overview_raw = details.get("overview") or (
        "No description available" if lang == "en" else "Описание отсутствует"
    )
    overview = escape(overview_raw)

    release_label = "Release Date" if lang == "en" else "Дата выхода"
    rating_label = "Rating" if lang == "en" else "Рейтинг"
    genres_label = "Genres" if lang == "en" else "Жанры"
    directors_label = "Directors" if lang == "en" else "Режиссёры"
    actors_label = "Actors" if lang == "en" else "Актёры"

    text = (
        f"🎬 <b>{title}</b>"
        + (f" (<b>{original}</b>)" if original and original != title else "")
        + "\n"
        f"📅 {escape(release_label)}: <b>{release_date}</b>\n"
        f"⭐ {escape(rating_label)}: <b>{rating}</b>\n"
        f"🎭 {escape(genres_label)}: <b>{genres_text}</b>\n\n"
        f"<blockquote expandable>{overview}</blockquote>\n\n"
        f"🎬 <b>{escape(directors_label)}:</b> / <code>👥 <b>{escape(actors_label)}:</b></code>"
    )

    markup = _build_movie_markup(
        user_id=user_id,
        movie_id=movie_id,
        credits=credits,
        viewer_id=viewer_id,
        lang=lang,
    )

    if details.get("poster_path"):
        poster = "https://image.tmdb.org/t/p/w500" + details["poster_path"]
        _send_photo_or_fallback(chat_id, poster, text, markup)
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
