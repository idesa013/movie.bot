from datetime import datetime

from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from loader import bot
from config_data.config import DATE_FORMAT

from api.tmdb_actor import get_actor_movie_credits
from database.actor_favorites import add_actor_favorite, remove_actor_favorite, check_actor_favorite
from keyboards.inline.add_to_actor_fav import add_actor_favorites_button
from keyboards.inline.actor_movies import actor_movies_markup
from utils.i18n import get_user_language, tmdb_language
from utils.admin_context import resolve_effective_user_id, has_selected_user, get_selected_user, get_selected_page


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


def _build_actor_markup(viewer_id: int, target_user_id: int, actor_id: int) -> InlineKeyboardMarkup:
    lang = get_user_language(target_user_id)
    tmdb_lang = tmdb_language(lang)

    credits = get_actor_movie_credits(actor_id, language=tmdb_lang) or {}
    movies = _sorted_movies_no_docs((credits.get("cast") or []), limit=10)

    movies_markup = actor_movies_markup(movies)
    in_favorites = check_actor_favorite(target_user_id, actor_id)
    fav_markup = add_actor_favorites_button(actor_id, in_favorites=in_favorites, lang=lang)
    merged = _merge_markups(movies_markup, fav_markup)

    if has_selected_user(viewer_id):
        back_text = "⬅ Back to User" if lang == "en" else "⬅ Назад к пользователю"
        merged.row(InlineKeyboardButton(back_text, callback_data=f"admin_user_back_to_card:{get_selected_user(viewer_id)}:{get_selected_page(viewer_id)}"))
    return merged


@bot.callback_query_handler(func=lambda call: call.data.startswith(("add_actor_fav:", "remove_actor_fav:")))
def handle_actor_favorites(call: CallbackQuery):
    viewer_id = call.from_user.id
    user_id = resolve_effective_user_id(viewer_id)
    actor_id = int(call.data.split(":")[1])

    if call.data.startswith("add_actor_fav:"):
        search_time = datetime.now().strftime(DATE_FORMAT)
        add_actor_favorite(user_id, actor_id, search_time)
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=_build_actor_markup(viewer_id, user_id, actor_id),
        )
        bot.answer_callback_query(call.id, "OK")
        return

    if call.data.startswith("remove_actor_fav:"):
        remove_actor_favorite(user_id, actor_id)
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=_build_actor_markup(viewer_id, user_id, actor_id),
        )
        bot.answer_callback_query(call.id, "OK")
        return
