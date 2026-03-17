from telebot.types import Message

from api.tmdb_actor import search_actor, get_actor_movie_credits
from loader import bot
from states.actor import ActorSearchState
from utils.access import ensure_user_not_blocked
from utils.i18n import get_user_language, tmdb_language, t
from utils.menu_router import route_menu_or_command
from utils.person_service import send_actor_card
from utils.search_helpers import pick_best_person_result


def _has_non_doc_actor_movies(actor_id: int, tmdb_lang: str) -> bool:
    credits = get_actor_movie_credits(actor_id, language=tmdb_lang) or {}
    cast = credits.get("cast", []) or []
    non_doc = [movie for movie in cast if 99 not in (movie.get("genre_ids") or [])]
    return len(non_doc) > 0


@bot.message_handler(
    state=ActorSearchState.waiting_for_actor_name,
    content_types=["text"],
)
def process_actor_search(message: Message):
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
        bot.send_message(chat_id, t(lang, "enter_actor_name"))
        return

    data = search_actor(query, language=tmdb_lang)
    results = data.get("results") or []

    if not results:
        bot.send_message(chat_id, t(lang, "actor_not_found_retry"))
        return

    actor_id = pick_best_person_result(
        results=results,
        query=query,
        department="Acting",
        validator=_has_non_doc_actor_movies,
        tmdb_lang=tmdb_lang,
    )

    if not actor_id:
        bot.send_message(chat_id, t(lang, "actor_not_found_retry"))
        return

    send_actor_card(
        chat_id,
        user_id,
        actor_id,
        searched_from="actor",
    )

    bot.delete_state(user_id, chat_id)
