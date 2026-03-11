import sqlite3
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from loader import bot
from database.db import DB_PATH
from database.bot_config import get_config_int
from api.tmdb_movie import get_movie_details
from api.tmdb_actor import get_actor_details
from api.tmdb_director import get_director_details
from keyboards.reply.main_menu import _TEXT
from utils.i18n import get_user_language, tmdb_language, ensure_registered
from utils.admin_context import (
    resolve_effective_user_id,
    has_selected_user,
    get_selected_user,
    get_selected_page,
)


def _title_units(title: str) -> int:
    title = (title or "").strip()
    ln = len(title)
    if ln <= 14:
        return 1
    if ln <= 24:
        return 2
    return 3


def _fav_limit(fav_type: str) -> int:
    mapping = {
        "movies": ("qty_movie_fav", 30),
        "actors": ("qty_actor_fav", 20),
        "directors": ("qty_director_fav", 10),
    }
    param_name, default = mapping[fav_type]
    return get_config_int(param_name, default)


def _build_markup(
    items: list[dict], callback_builder, viewer_id: int, lang: str
) -> InlineKeyboardMarkup:
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
        btn = InlineKeyboardButton(
            text=title, callback_data=callback_data, style="primary"
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

    if has_selected_user(viewer_id):
        back_text = "⬅ Back to User" if lang == "en" else "⬅ Назад к пользователю"
        markup.row(
            InlineKeyboardButton(
                back_text,
                callback_data=f"admin_user_back_to_card:{get_selected_user(viewer_id)}:{get_selected_page(viewer_id)}",
            )
        )

    return markup


def _load_items_for_fav_type(user_id: int, fav_type: str, lang: str) -> list[dict]:
    tmdb_lang = tmdb_language(lang)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if fav_type == "movies":
        cur.execute(
            "SELECT movie_id FROM favorites WHERE user_id = ? ORDER BY search_time DESC",
            (user_id,),
        )
        ids = [row[0] for row in cur.fetchall()]
        conn.close()

        items = []
        seen = set()
        for movie_id in ids:
            if movie_id in seen:
                continue
            seen.add(movie_id)
            details = get_movie_details(movie_id, language=tmdb_lang) or {}
            title = details.get("title") or details.get("original_title")
            if title:
                items.append({"id": movie_id, "title": title})
        return items

    if fav_type == "actors":
        cur.execute(
            "SELECT actor_id FROM actor_favorites WHERE user_id = ? ORDER BY search_time DESC",
            (user_id,),
        )
        ids = [row[0] for row in cur.fetchall()]
        conn.close()

        items = []
        seen = set()
        for actor_id in ids:
            if actor_id in seen:
                continue
            seen.add(actor_id)
            details = get_actor_details(actor_id, language=tmdb_lang) or {}
            name = details.get("name")
            if name:
                items.append({"id": actor_id, "title": name})
        return items

    cur.execute(
        "SELECT director_id FROM director_favorites WHERE user_id = ? ORDER BY search_time DESC",
        (user_id,),
    )
    ids = [row[0] for row in cur.fetchall()]
    conn.close()

    items = []
    seen = set()
    for director_id in ids:
        if director_id in seen:
            continue
        seen.add(director_id)
        details = get_director_details(director_id, language=tmdb_lang) or {}
        name = details.get("name")
        if name:
            items.append({"id": director_id, "title": name})
    return items


def send_favorites_list(
    chat_id: int, viewer_id: int, target_user_id: int, fav_type: str, edit_message=None
):
    lang = get_user_language(target_user_id)
    limit = _fav_limit(fav_type)

    if fav_type == "movies":
        items = _load_items_for_fav_type(target_user_id, "movies", lang)
        title_text = (
            f"🎬 Favorite movies ({len(items)} of {limit}):"
            if lang == "en"
            else f"🎬 Избранные фильмы ({len(items)} из {limit}):"
        )
        callback_builder = lambda movie_id: f"movie_{movie_id}_movie"

    elif fav_type == "actors":
        items = _load_items_for_fav_type(target_user_id, "actors", lang)
        title_text = (
            f"🎭 Favorite actors ({len(items)} of {limit}):"
            if lang == "en"
            else f"🎭 Избранные актеры ({len(items)} из {limit}):"
        )
        callback_builder = lambda actor_id: f"actor_{actor_id}"

    else:
        items = _load_items_for_fav_type(target_user_id, "directors", lang)
        title_text = (
            f"🎬 Favorite directors ({len(items)} of {limit}):"
            if lang == "en"
            else f"🎬 Избранные режиссеры ({len(items)} из {limit}):"
        )
        callback_builder = lambda director_id: f"director_{director_id}"

    if not items:
        empty_text = {
            "movies": (
                f"🎬 Избранные фильмы (0 из {limit}):"
                if lang == "ru"
                else f"🎬 Favorite movies (0 of {limit}):"
            ),
            "actors": (
                f"🎭 Избранные актеры (0 из {limit}):"
                if lang == "ru"
                else f"🎭 Favorite actors (0 of {limit}):"
            ),
            "directors": (
                f"🎬 Избранные режиссеры (0 из {limit}):"
                if lang == "ru"
                else f"🎬 Favorite directors (0 of {limit}):"
            ),
        }[fav_type]

        markup = None
        if has_selected_user(viewer_id):
            markup = InlineKeyboardMarkup()
            back_text = "⬅ Back to User" if lang == "en" else "⬅ Назад к пользователю"
            markup.row(
                InlineKeyboardButton(
                    back_text,
                    callback_data=f"admin_user_back_to_card:{get_selected_user(viewer_id)}:{get_selected_page(viewer_id)}",
                )
            )

        if edit_message:
            try:
                bot.edit_message_text(
                    empty_text,
                    chat_id,
                    edit_message.message_id,
                    reply_markup=markup,
                )
                return
            except Exception:
                pass

        bot.send_message(chat_id, empty_text, reply_markup=markup)
        return

    markup = _build_markup(items, callback_builder, viewer_id, lang)

    if edit_message:
        try:
            bot.edit_message_text(
                title_text,
                chat_id,
                edit_message.message_id,
                reply_markup=markup,
            )
            return
        except Exception:
            pass

    bot.send_message(chat_id, title_text, reply_markup=markup)


@bot.message_handler(
    func=lambda m: (m.text or "").strip()
    in (_TEXT["en"]["fav_movies"], _TEXT["ru"]["fav_movies"])
)
def show_favorite_movies(message: Message):
    if not ensure_registered(bot, message.chat.id, message.from_user.id):
        return

    viewer_id = message.from_user.id
    user_id = resolve_effective_user_id(viewer_id)
    send_favorites_list(message.chat.id, viewer_id, user_id, "movies")


@bot.message_handler(
    func=lambda m: (m.text or "").strip()
    in (_TEXT["en"]["fav_actors"], _TEXT["ru"]["fav_actors"])
)
def show_favorite_actors(message: Message):
    if not ensure_registered(bot, message.chat.id, message.from_user.id):
        return

    viewer_id = message.from_user.id
    user_id = resolve_effective_user_id(viewer_id)
    send_favorites_list(message.chat.id, viewer_id, user_id, "actors")


@bot.message_handler(
    func=lambda m: (m.text or "").strip()
    in (_TEXT["en"]["fav_directors"], _TEXT["ru"]["fav_directors"])
)
def show_favorite_directors(message: Message):
    if not ensure_registered(bot, message.chat.id, message.from_user.id):
        return

    viewer_id = message.from_user.id
    user_id = resolve_effective_user_id(viewer_id)
    send_favorites_list(message.chat.id, viewer_id, user_id, "directors")
