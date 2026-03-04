from datetime import datetime

from telebot.types import CallbackQuery, InlineKeyboardMarkup

from loader import bot
from config_data.config import DATE_FORMAT

from api.tmdb_director import get_director_movie_credits
from database.director_favorites import (
    add_director_favorite,
    remove_director_favorite,
    check_director_favorite,
)
from keyboards.inline.add_to_director_fav import add_director_favorites_button
from keyboards.inline.director_movies import director_movies_markup
from utils.i18n import get_user_language, tmdb_language


def _sorted_movies_no_docs(movies: list, limit: int = 10) -> list:
    filtered = [m for m in movies if 99 not in m.get("genre_ids", [])]
    return sorted(filtered, key=lambda m: m.get("popularity", 0), reverse=True)[:limit]


def _merge_markups(top: InlineKeyboardMarkup, bottom: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    merged = InlineKeyboardMarkup()
    for row in top.keyboard or []:
        merged.row(*row)
    for row in bottom.keyboard or []:
        merged.row(*row)
    return merged


def _build_director_markup(user_id: int, director_id: int) -> InlineKeyboardMarkup:
    lang = get_user_language(user_id)
    tmdb_lang = tmdb_language(lang)

    credits = get_director_movie_credits(director_id, language=tmdb_lang) or {}
    crew = credits.get("crew", []) or []
    directed = [m for m in crew if m.get("job") == "Director"]
    movies = _sorted_movies_no_docs(directed, limit=10)

    movies_markup = director_movies_markup(movies)
    in_favorites = check_director_favorite(user_id, director_id)
    fav_markup = add_director_favorites_button(director_id, in_favorites=in_favorites, lang=lang)

    return _merge_markups(movies_markup, fav_markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith(("add_director_fav:", "remove_director_fav:")))
def handle_director_favorites(call: CallbackQuery):
    user_id = call.from_user.id
    director_id = int(call.data.split(":")[1])

    if call.data.startswith("add_director_fav:"):
        search_time = datetime.now().strftime(DATE_FORMAT)
        add_director_favorite(user_id, director_id, search_time)
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=_build_director_markup(user_id, director_id),
        )
        bot.answer_callback_query(call.id, "OK")
        return

    if call.data.startswith("remove_director_fav:"):
        remove_director_favorite(user_id, director_id)
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=_build_director_markup(user_id, director_id),
        )
        bot.answer_callback_query(call.id, "OK")
        return
