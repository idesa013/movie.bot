from datetime import datetime

from telebot.types import Message

from api.tmdb_movie import search_movie
from config_data.config import DATE_FORMAT
from loader import bot
from states.movie import MovieSearchState
from utils.access import ensure_user_not_blocked
from utils.i18n import get_user_language, tmdb_language, t
from utils.menu_router import route_menu_or_command
from utils.movie_service import send_movie_card
from utils.search_helpers import pick_exact_or_first


@bot.message_handler(state=MovieSearchState.waiting_for_title, content_types=["text"])
def search_movie_handler(message: Message):
    if not ensure_user_not_blocked(bot, message.chat.id, message.from_user.id):
        return

    if route_menu_or_command(bot, message):
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    lang = get_user_language(user_id)
    tmdb_lang = tmdb_language(lang)

    query = (message.text or "").strip()

    if not query:
        bot.send_message(chat_id, t(lang, "enter_movie_title"))
        return

    data = search_movie(query, language=tmdb_lang)
    results = data.get("results") or []

    if not results:
        bot.send_message(chat_id, t(lang, "movie_not_found_retry"))
        return

    best_result = pick_exact_or_first(results, query)
    if not best_result:
        bot.send_message(chat_id, t(lang, "movie_not_found_retry"))
        return

    movie_id = best_result.get("id")
    if not movie_id:
        bot.send_message(chat_id, t(lang, "movie_not_found_retry"))
        return

    search_time = datetime.fromtimestamp(message.date).strftime(DATE_FORMAT)

    send_movie_card(
        chat_id,
        int(movie_id),
        user_id,
        searched_from="movie",
        search_time=search_time,
    )

    bot.delete_state(user_id, chat_id)
