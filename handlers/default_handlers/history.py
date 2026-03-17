from __future__ import annotations

from email import header
from html import escape

from telebot.types import Message

from loader import bot
from database.history import get_user_history
from utils.access import ensure_user_not_blocked
from utils.i18n import get_user_language, tmdb_language, LANG_RU

from keyboards.reply.admin_menu import get_main_menu

from api.tmdb_movie import get_movie_details
from api.tmdb_actor import get_actor_details
from api.tmdb_director import get_director_details


HISTORY_TEXT = {
    "title": {
        "ru": "<b>История запросов:</b>",
        "en": "<b>Search history:</b>",
    },
    "empty": {
        "ru": "История запросов пуста.",
        "en": "Search history is empty.",
    },
    "date": {
        "ru": "Дата/Время",
        "en": "Date/Time",
    },
    "type": {
        "ru": "Тип",
        "en": "Type",
    },
    "name": {
        "ru": "Название/Имя",
        "en": "Title/Name",
    },
    "source": {
        "ru": "Откуда",
        "en": "From",
    },
    "fav": {
        "ru": "Избранное",
        "en": "Favorite",
    },
    "movie": {
        "ru": "фильм",
        "en": "movie",
    },
    "actor": {
        "ru": "актёр",
        "en": "actor",
    },
    "director": {
        "ru": "режиссёр",
        "en": "director",
    },
    "src_movie": {
        "ru": "фильм",
        "en": "movie",
    },
    "src_actor": {
        "ru": "актёр",
        "en": "actor",
    },
    "src_director": {
        "ru": "режиссёр",
        "en": "director",
    },
    "src_unknown": {
        "ru": "-",
        "en": "-",
    },
}


def ht(lang: str, key: str) -> str:
    lang = "ru" if lang == "ru" else "en"
    return HISTORY_TEXT[key][lang]


def _call_with_language(func, entity_id: int, user_lang: str) -> dict:
    """
    Поддерживает оба варианта:
    1) если твоя функция уже принимает language=
    2) если пока ещё нет — тогда просто вызывает по старому
    """
    try:
        return func(entity_id, language=tmdb_language(user_lang)) or {}
    except TypeError:
        return func(entity_id) or {}
    except Exception:
        return {}


def _resolve_display_name(entity_type: str, entity_id: int, user_lang: str) -> str:
    if entity_type == "movie":
        data = _call_with_language(get_movie_details, entity_id, user_lang)
        return (
            data.get("title")
            or data.get("name")
            or data.get("original_title")
            or f"ID:{entity_id}"
        )

    if entity_type == "actor":
        data = _call_with_language(get_actor_details, entity_id, user_lang)
        return data.get("name") or f"ID:{entity_id}"

    if entity_type == "director":
        data = _call_with_language(get_director_details, entity_id, user_lang)
        return data.get("name") or f"ID:{entity_id}"

    return f"ID:{entity_id}"


def _source_label(source: str, lang: str) -> str:
    source_map = {
        "movie": ht(lang, "src_movie"),
        "actor": ht(lang, "src_actor"),
        "director": ht(lang, "src_director"),
        "str": ht(lang, "src_unknown"),
        "": ht(lang, "src_unknown"),
        None: ht(lang, "src_unknown"),
    }
    return source_map.get(source, str(source))


def _entity_label(entity_type: str, lang: str) -> str:
    if entity_type == "movie":
        return ht(lang, "movie")
    if entity_type == "actor":
        return ht(lang, "actor")
    if entity_type == "director":
        return ht(lang, "director")
    return entity_type


@bot.message_handler(commands=["history"])
def show_history(message: Message):
    if not ensure_user_not_blocked(bot, message.chat.id, message.from_user.id):
        return

    user_id = message.from_user.id
    lang = get_user_language(user_id)

    rows = get_user_history(user_id=user_id, limit=20)
    if not rows:
        bot.send_message(message.chat.id, ht(lang, "empty"))
        return

    header = (
        f"{ht(lang, 'date'):<16} | "
        f"{ht(lang, 'type'):<8} | "
        f"{ht(lang, 'source'):<8} | "
        f"{ht(lang, 'fav')}"
    )
    separator = "-" * len(header)
    lines = [header, separator]

    for row in rows:
        entity_type = row["entity_type"]
        entity_id = int(row["entity_id"])
        search_time = str(row["search_time"])[:19]
        searched_from = row.get("searched_from")
        in_favorites = bool(row.get("in_favorites"))

        display_name = _resolve_display_name(entity_type, entity_id, lang)
        display_name = display_name.replace("\n", " ").strip()

        type_label = _entity_label(entity_type, lang)
        source_label = _source_label(searched_from, lang)
        fav_mark = "★" if in_favorites else "-"

        lines.append(
            f"{search_time:<16} | "
            f"{type_label:<8} | "
            f"{source_label:<8} | "
            f"{fav_mark}"
            f"\n{ht(lang, 'name')}:  {display_name[:28]} "
            f"{separator}"
        )

    text = f"{ht(lang, 'title')}\n<pre>{escape(chr(10).join(lines))}</pre>"
    bot.send_message(
        message.chat.id,
        text,
        parse_mode="HTML",
        reply_markup=get_main_menu(message.from_user.id, lang),
    )
