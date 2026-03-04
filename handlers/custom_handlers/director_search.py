from telebot.types import Message

from loader import bot
from states.director import DirectorSearchState
from states.movie import MovieSearchState
from states.actor import ActorSearchState
from api.tmdb_director import search_director
from utils.person_service import send_director_card
from utils.i18n import get_user_language, tmdb_language, t


_MENU_MOVIE_EN = "🎬 Movie Search"
_MENU_ACTOR_EN = "🎭 Search Actor"
_MENU_DIRECTOR_EN = "🎬 Search Director"

_MENU_MOVIE_RU = "🎬 Поиск фильма"
_MENU_ACTOR_RU = "🎭 Поиск актёра"
_MENU_DIRECTOR_RU = "🎬 Поиск режиссёра"


def _route_menu_text_in_state(message: Message, lang: str) -> bool:
    txt = (message.text or "").strip()

    if txt in (_MENU_MOVIE_EN, _MENU_MOVIE_RU):
        bot.set_state(
            message.from_user.id, MovieSearchState.waiting_for_title, message.chat.id
        )
        bot.send_message(
            message.chat.id,
            "Введите название фильма:" if lang == "ru" else "Enter the movie title:",
        )
        return True

    if txt in (_MENU_ACTOR_EN, _MENU_ACTOR_RU):
        bot.set_state(
            message.from_user.id,
            ActorSearchState.waiting_for_actor_name,
            message.chat.id,
        )
        bot.send_message(
            message.chat.id,
            "Введите имя актёра:" if lang == "ru" else "Enter the actor name:",
        )
        return True

    if txt in (_MENU_DIRECTOR_EN, _MENU_DIRECTOR_RU):
        bot.set_state(
            message.from_user.id,
            DirectorSearchState.waiting_for_director_name,
            message.chat.id,
        )
        bot.send_message(
            message.chat.id,
            "Введите имя режиссёра:" if lang == "ru" else "Enter the director name:",
        )
        return True

    return False


@bot.message_handler(state=DirectorSearchState.waiting_for_director_name)
def process_director_search(message: Message):
    lang = get_user_language(message.from_user.id)

    if _route_menu_text_in_state(message, lang):
        return

    query = (message.text or "").strip()
    if not query:
        return

    tmdb_lang = tmdb_language(lang)

    data = search_director(query, language=tmdb_lang)
    results = data.get("results") or []
    if not results:
        bot.send_message(message.chat.id, t(lang, "director_not_found"))
        return

    director_id = results[0].get("id")
    if not director_id:
        bot.send_message(message.chat.id, t(lang, "director_not_found"))
        return

    send_director_card(
        message.chat.id, message.from_user.id, int(director_id), searched_from="str"
    )
    bot.delete_state(message.from_user.id, message.chat.id)
