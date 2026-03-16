from datetime import datetime

from telebot.types import Message

from api.tmdb_movie import search_movie
from loader import bot
from states.movie import MovieSearchState

from utils.movie_service import send_movie_card
from utils.i18n import get_user_language, tmdb_language, t
from utils.menu_router import route_menu_or_command
from utils.access import ensure_user_not_blocked

from config_data.config import DATE_FORMAT


def _normalize_text(value: str) -> str:
    """
    Нормализует текст для сравнения
    """
    return " ".join((value or "").strip().lower().split())


def _pick_best_movie_result(results: list[dict], query: str) -> dict | None:
    """
    Выбирает лучший результат поиска
    """
    normalized_query = _normalize_text(query)

    for item in results:
        title = _normalize_text(item.get("title", ""))
        original_title = _normalize_text(item.get("original_title", ""))

        if normalized_query == title or normalized_query == original_title:
            return item

    return results[0] if results else None


@bot.message_handler(state=MovieSearchState.waiting_for_title, content_types=["text"])
def search_movie_handler(message: Message):

    if not ensure_user_not_blocked(bot, message.chat.id, message.from_user.id):
        return

    if route_menu_or_command(bot, message):
        return

    lang = get_user_language(message.from_user.id)
    tmdb_lang = tmdb_language(lang)

    query = (message.text or "").strip()

    if not query:
        bot.send_message(
            message.chat.id,
            t(lang, "enter_movie_title"),
        )
        return

    data = search_movie(
        query,
        language=tmdb_lang,
    )

    results = data.get("results") or []

    if not results:
        bot.send_message(
            message.chat.id,
            t(lang, "movie_not_found_retry"),
        )
        return

    best_result = _pick_best_movie_result(results, query)

    if not best_result:
        bot.send_message(
            message.chat.id,
            t(lang, "movie_not_found_retry"),
        )
        return

    movie_id = best_result.get("id")

    search_time = datetime.fromtimestamp(message.date).strftime(DATE_FORMAT)

    send_movie_card(
        message.chat.id,
        movie_id,
        message.from_user.id,
        searched_from="movie",
        search_time=search_time,
    )

    bot.delete_state(message.from_user.id, message.chat.id)
