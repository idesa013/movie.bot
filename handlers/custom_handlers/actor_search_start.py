from telebot.types import Message

from loader import bot
from states.actor import ActorSearchState
from api.tmdb_actor import search_actor, get_actor_movie_credits
from utils.person_service import send_actor_card
from utils.i18n import get_user_language, tmdb_language, t, route_menu_or_command


def _has_non_doc_actor_movies(actor_id: int, tmdb_lang: str) -> bool:
    """
    True если у персоны реально есть фильмы (cast) и среди них есть НЕ документальные.
    Документальные в TMDB обычно genre_id = 99.
    """
    credits = get_actor_movie_credits(actor_id, language=tmdb_lang) or {}
    cast = credits.get("cast", []) or []
    non_doc = [m for m in cast if 99 not in (m.get("genre_ids") or [])]
    return len(non_doc) > 0


@bot.message_handler(
    state=ActorSearchState.waiting_for_actor_name, content_types=["text"]
)
def process_actor_search(message: Message):
    if route_menu_or_command(bot, message):
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    lang = get_user_language(user_id)
    tmdb_lang = tmdb_language(lang)

    query = (message.text or "").strip()
    if not query:
        return

    data = search_actor(query, language=tmdb_lang)
    results = data.get("results") or []
    if not results:
        bot.send_message(chat_id, t(lang, "actor_not_found"))
        return

    # 1) берём только Acting
    actors = [p for p in results if p.get("known_for_department") == "Acting"]
    actors.sort(key=lambda x: x.get("popularity", 0), reverse=True)

    # 2) валидируем через credits (есть НЕ документальные фильмы в cast)
    actor_id = None
    for p in actors[:12]:
        pid = p.get("id")
        if not pid:
            continue
        if _has_non_doc_actor_movies(int(pid), tmdb_lang):
            actor_id = int(pid)
            break

    if not actor_id:
        bot.send_message(chat_id, t(lang, "actor_not_found"))
        return

    # ✅ searched_from для прямого поиска актёра (вместо "str")
    send_actor_card(chat_id, user_id, actor_id, searched_from="actor")
    bot.delete_state(user_id, chat_id)
