from datetime import datetime
from html import escape

from loader import bot
from config_data.config import DATE_FORMAT

from api.tmdb_movie import get_movie_details, get_movie_credits
from database.favorites import check_favorite
from database.logs import log_movie_search

from keyboards.inline.add_to_fav import add_favorites_button
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.i18n import get_user_language, tmdb_language, t, LANG_RU


def _chunked(items, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _build_movie_markup(user_id: int, movie_id: int, credits: dict) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()

    # 1) Directors — up to 3 per row
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

    # 2) Actors — up to 3 per row (style primary)
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
        InlineKeyboardButton(text=name, callback_data=f"actor_{act_id}", style="primary")
        for act_id, name in actors
    ]
    for row in _chunked(actor_buttons, 3):
        markup.row(*row)

    # 3) Favorites button last row (success/danger preserved in add_favorites_button)
    in_favorites = check_favorite(user_id, movie_id)
    fav_markup = add_favorites_button(movie_id, in_favorites=in_favorites, lang=get_user_language(user_id))
    for row in fav_markup.keyboard:
        markup.row(*row)

    return markup


def _fallback_en_if_missing_ru(field_ru: str, field_en: str, lang: str) -> str:
    # When UI is Russian and Russian field missing -> show notice then English
    if lang == LANG_RU and not (field_ru or "").strip() and (field_en or "").strip():
        return f"{t(lang, 'no_ru_info_fallback')}\n{field_en}"
    return field_ru


def send_movie_card(
    chat_id: int,
    movie_id: int,
    user_id: int,
    searched_from: str = "movie",
    search_time: str | None = None,
):
    lang = get_user_language(user_id)
    tmdb_lang = tmdb_language(lang)

    details = get_movie_details(movie_id, language=tmdb_lang) or {}
    credits = get_movie_credits(movie_id, language=tmdb_lang) or {}

    # English details for fallback (only if needed)
    details_en = None

    if not search_time:
        search_time = datetime.now().strftime(DATE_FORMAT)

    # genres + ids for logs
    genres = details.get("genres", []) or []
    genres_text = ", ".join(escape(g.get("name", "")) for g in genres if g.get("name")) or "n/a"
    genre_ids_str = " ".join(str(g["id"]) for g in genres if g.get("id") is not None) if genres else ""

    log_movie_search(user_id, movie_id, search_time, genre_ids_str, searched_from=searched_from)

    title_ru = (details.get("title") or "").strip()
    original_ru = (details.get("original_title") or "").strip()
    overview_ru = (details.get("overview") or "").strip()

    if lang == LANG_RU and (not title_ru or not overview_ru):
        details_en = get_movie_details(movie_id, language="en-US") or {}

    title = title_ru
    original = original_ru
    overview_raw = overview_ru

    if details_en:
        title = _fallback_en_if_missing_ru(title_ru, (details_en.get("title") or "").strip(), lang)
        overview_raw = _fallback_en_if_missing_ru(overview_ru, (details_en.get("overview") or "").strip(), lang)

    if not (overview_raw or "").strip():
        overview_raw = t(lang, "no_overview")

    overview = escape(overview_raw)

    release_date = escape(details.get("release_date", "n/a"))
    rating = details.get("vote_average", "n/a")

    # lines
    text = (
        f"🎬 <b>{escape(title)}</b>"
        + (f" (<b>{escape(original)}</b>)" if original and original != title else "")
        + "\n"
        f"{t(lang, 'release_date')} <b>{release_date}</b>\n"
        f"{t(lang, 'rating')} <b>{rating}</b>\n"
        f"{t(lang, 'genres')} <b>{genres_text}</b>\n\n"
        f"<blockquote expandable>{overview}</blockquote>\n\n"
        f"{t(lang, 'directors')} / <code>{t(lang, 'actors')}</code>"
    )

    markup = _build_movie_markup(user_id=user_id, movie_id=movie_id, credits=credits)

    if details.get("poster_path"):
        poster = "https://image.tmdb.org/t/p/w500" + details["poster_path"]
        bot.send_photo(chat_id, poster, caption=text, parse_mode="HTML", reply_markup=markup)
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
