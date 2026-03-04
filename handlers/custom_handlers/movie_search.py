from datetime import datetime
import requests
from telebot.types import Message

from loader import bot
from config_data.config import DATE_FORMAT, TMBD_API_KEY
from states.movie import MovieSearchState
from states.actor import ActorSearchState
from states.director import DirectorSearchState
from utils.movie_service import send_movie_card
from utils.i18n import get_user_language, tmdb_language, t


# тексты кнопок главного меню (как в keyboards/reply/main_menu.py)
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


@bot.message_handler(state=MovieSearchState.waiting_for_title)
def search_movie(message: Message):
    lang = get_user_language(message.from_user.id)

    # ✅ если нажали кнопку меню — переключаем сценарий, не ищем как текст
    if _route_menu_text_in_state(message, lang):
        return

    query = (message.text or "").strip()
    if not query:
        return

    tmdb_lang = tmdb_language(lang)

    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMBD_API_KEY, "query": query, "language": tmdb_lang}

    r = requests.get(url, params=params, timeout=12).json()
    results = r.get("results") or []

    if not results:
        # ✅ state НЕ сбрасываем — можно сразу вводить другой запрос
        bot.send_message(message.chat.id, t(lang, "movie_not_found"))
        return

    movie_id = results[0].get("id")
    search_time = datetime.fromtimestamp(message.date).strftime(DATE_FORMAT)

    send_movie_card(
        message.chat.id,
        movie_id,
        message.from_user.id,
        searched_from="movie",
        search_time=search_time,
    )

    bot.delete_state(message.from_user.id, message.chat.id)
