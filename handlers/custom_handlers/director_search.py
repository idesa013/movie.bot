from telebot.types import Message

from loader import bot
from states.director import DirectorSearchState
from api.tmdb_director import search_director, get_director_movie_credits
from utils.person_service import send_director_card
from utils.i18n import get_user_language, tmdb_language, t, route_menu_or_command
from utils.access import ensure_user_not_blocked


def _has_directed_movies(person_id: int, tmdb_lang: str) -> bool:
    credits = get_director_movie_credits(person_id, language=tmdb_lang) or {}
    crew = credits.get("crew", []) or []
    return any(x.get("job") == "Director" for x in crew)


@bot.message_handler(
    state=DirectorSearchState.waiting_for_director_name, content_types=["text"]
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
        return

    # защита от меню-кнопки внутри state
    if query in ("🎬 Search Director", "🎬 Поиск режиссёра"):
        bot.send_message(
            chat_id,
            "Enter director name:" if lang == "en" else "Введите имя режиссёра:",
        )
        return

    data = search_director(query, language=tmdb_lang)
    results = data.get("results") or []
    if not results:
        bot.send_message(chat_id, t(lang, "director_not_found"))
        return

    directors = [p for p in results if p.get("known_for_department") == "Directing"]
    directors.sort(key=lambda x: x.get("popularity", 0), reverse=True)

    director_id = None
    for p in directors[:10]:
        pid = p.get("id")
        if not pid:
            continue
        if _has_directed_movies(int(pid), tmdb_lang):
            director_id = int(pid)
            break

    if not director_id:
        bot.send_message(chat_id, t(lang, "director_not_found"))
        return

    send_director_card(chat_id, user_id, director_id, searched_from="director")
    bot.delete_state(user_id, chat_id)