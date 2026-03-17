from telebot.types import Message

from api.tmdb_director import search_director, get_director_movie_credits
from loader import bot
from states.director import DirectorSearchState
from utils.access import ensure_user_not_blocked
from utils.i18n import get_user_language, tmdb_language, t
from utils.menu_router import route_menu_or_command
from utils.person_service import send_director_card
from utils.search_helpers import pick_best_person_result


def _has_directed_movies(person_id: int, tmdb_lang: str) -> bool:
    credits = get_director_movie_credits(person_id, language=tmdb_lang) or {}
    crew = credits.get("crew", []) or []
    return any(item.get("job") == "Director" for item in crew)


@bot.message_handler(
    state=DirectorSearchState.waiting_for_director_name,
    content_types=["text"],
)
def process_director_search(message: Message):
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
        bot.send_message(chat_id, t(lang, "enter_director_name"))
        return

    data = search_director(query, language=tmdb_lang)
    results = data.get("results") or []

    if not results:
        bot.send_message(chat_id, t(lang, "director_not_found_retry"))
        return

    director_id = pick_best_person_result(
        results=results,
        query=query,
        department="Directing",
        validator=_has_directed_movies,
        tmdb_lang=tmdb_lang,
    )

    if not director_id:
        bot.send_message(chat_id, t(lang, "director_not_found_retry"))
        return

    send_director_card(
        chat_id,
        user_id,
        director_id,
        searched_from="director",
    )

    bot.delete_state(user_id, chat_id)
