from datetime import datetime
from html import escape

from telebot.types import InlineKeyboardMarkup

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

from utils.i18n import get_user_language, tmdb_language


CAPTION_LIMIT = 1024  # Telegram caption limit (practically)


def _sorted_movies_no_docs(movies: list, limit: int = 10) -> list:
    filtered = [m for m in movies if 99 not in (m.get("genre_ids") or [])]
    return sorted(filtered, key=lambda m: m.get("popularity", 0), reverse=True)[:limit]


def _merge_markups(
    top: InlineKeyboardMarkup, bottom: InlineKeyboardMarkup
) -> InlineKeyboardMarkup:
    merged = InlineKeyboardMarkup()
    for row in top.keyboard or []:
        merged.row(*row)
    for row in bottom.keyboard or []:
        merged.row(*row)
    return merged


def _movie_title_for_lang(movie: dict, lang: str) -> str:
    title = (movie.get("title") or "").strip()
    original = (movie.get("original_title") or "").strip()
    if lang == "en":
        return original or title or "Movie"
    return title or original or "Фильм"


def _bio_with_notice(details: dict, lang: str) -> tuple[str, str | None]:
    bio = (details.get("biography") or "").strip()
    if not bio:
        return ("No biography available" if lang == "en" else "Биографии нет", None)

    # Если выбрали RU, но отдали EN (fallback) — вставляем предупреждение
    if lang == "ru":
        bio_lang = (details.get("_bio_lang") or "").lower()
        fallback = (details.get("_bio_fallback_lang") or "").lower()
        if fallback == "en" or bio_lang.startswith("en"):
            return (bio, "На русском языке этой информации нет, есть на английском:")

    return (bio, None)


def _send_photo_or_message_one_or_two(
    chat_id: int, photo_url: str | None, text: str, markup
):
    if photo_url:
        if len(text) <= CAPTION_LIMIT:
            bot.send_photo(
                chat_id, photo_url, caption=text, parse_mode="HTML", reply_markup=markup
            )
            return

        bot.send_photo(chat_id, photo_url)
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
        return

    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)


def send_actor_card(
    chat_id: int, user_id: int, actor_id: int, searched_from: str = "movie"
):
    lang = get_user_language(user_id)
    tmdb_lang = tmdb_language(lang)

    details = get_actor_details(actor_id, language=tmdb_lang) or {}
    credits = get_actor_movie_credits(actor_id, language=tmdb_lang) or {}

    search_time = datetime.now().strftime(DATE_FORMAT)
    log_actor_search(user_id, actor_id, search_time, searched_from=searched_from)

    bio, notice = _bio_with_notice(details, lang)

    # Лейблы БЕЗ эмодзи (эмодзи добавляем 1 раз в шаблоне строк)
    birthday_label = "Birthday" if lang == "en" else "Дата рождения"
    pob_label = "Place of birth" if lang == "en" else "Место рождения"
    movies_label = "Movies" if lang == "en" else "Фильмы"

    name = escape(details.get("name", ""))
    birthday = escape(details.get("birthday") or ("n/a" if lang == "en" else "н/д"))
    pob = escape(details.get("place_of_birth") or ("n/a" if lang == "en" else "н/д"))

    notice_html = f"<b>{escape(notice)}</b>\n" if notice else ""
    text = (
        f"🎭 <b>{name}</b>\n"
        f"📅 {escape(birthday_label)}: <b>{birthday}</b>\n"
        f"🌍 {escape(pob_label)}: <b>{pob}</b>\n\n"
        f"{notice_html}<blockquote expandable>{escape(bio)}</blockquote>\n\n"
        f"🎬 <b>{escape(movies_label)}:</b>"
    )

    known_movies_raw = _sorted_movies_no_docs(credits.get("cast", []), limit=10)
    known_movies = []
    for m in known_movies_raw:
        mm = dict(m)
        mm["title"] = _movie_title_for_lang(mm, lang)
        known_movies.append(mm)

    movies_markup = actor_movies_markup(known_movies)
    in_favorites = check_actor_favorite(user_id, actor_id)
    fav_markup = add_actor_favorites_button(
        actor_id, in_favorites=in_favorites, lang=lang
    )
    markup = _merge_markups(movies_markup, fav_markup)

    photo = None
    if details.get("profile_path"):
        photo = "https://image.tmdb.org/t/p/w500" + details["profile_path"]

    _send_photo_or_message_one_or_two(chat_id, photo, text, markup)


def send_director_card(
    chat_id: int, user_id: int, director_id: int, searched_from: str = "movie"
):
    lang = get_user_language(user_id)
    tmdb_lang = tmdb_language(lang)

    details = get_director_details(director_id, language=tmdb_lang) or {}
    credits = get_director_movie_credits(director_id, language=tmdb_lang) or {}

    search_time = datetime.now().strftime(DATE_FORMAT)
    log_director_search(user_id, director_id, search_time, searched_from=searched_from)

    bio, notice = _bio_with_notice(details, lang)

    birthday_label = "Birthday" if lang == "en" else "Дата рождения"
    pob_label = "Place of birth" if lang == "en" else "Место рождения"
    directed_label = "Directed" if lang == "en" else "Фильмы (как режиссёр)"

    name = escape(details.get("name", ""))
    birthday = escape(details.get("birthday") or ("n/a" if lang == "en" else "н/д"))
    pob = escape(details.get("place_of_birth") or ("n/a" if lang == "en" else "н/д"))

    notice_html = f"<b>{escape(notice)}</b>\n" if notice else ""
    text = (
        f"🎬 <b>{name}</b>\n"
        f"📅 {escape(birthday_label)}: <b>{birthday}</b>\n"
        f"🌍 {escape(pob_label)}: <b>{pob}</b>\n\n"
        f"{notice_html}<blockquote expandable>{escape(bio)}</blockquote>\n\n"
        f"🎥 <b>{escape(directed_label)}:</b>"
    )

    crew = credits.get("crew", []) or []
    directed = [m for m in crew if m.get("job") == "Director"]
    known_movies_raw = _sorted_movies_no_docs(directed, limit=10)
    known_movies = []
    for m in known_movies_raw:
        mm = dict(m)
        mm["title"] = _movie_title_for_lang(mm, lang)
        known_movies.append(mm)

    movies_markup = director_movies_markup(known_movies)
    in_favorites = check_director_favorite(user_id, director_id)
    fav_markup = add_director_favorites_button(
        director_id, in_favorites=in_favorites, lang=lang
    )
    markup = _merge_markups(movies_markup, fav_markup)

    photo = None
    if details.get("profile_path"):
        photo = "https://image.tmdb.org/t/p/w500" + details["profile_path"]

    _send_photo_or_message_one_or_two(chat_id, photo, text, markup)
