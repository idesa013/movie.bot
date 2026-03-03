from telebot.types import Message
from loader import bot
from states.director import DirectorSearchState
from api.tmdb_director import search_director
from utils.person_service import send_director_card


@bot.message_handler(state=DirectorSearchState.waiting_for_director_name)
def process_director_search(message: Message):
    query = message.text

    data = search_director(query)
    results = data.get("results")
    if not results:
        bot.send_message(message.chat.id, "Director not found")
        return

    # Пытаемся выбрать именно режиссёра, если TMDB отдал разных людей
    director = None
    for r in results:
        if (r.get("known_for_department") or "").lower() == "directing":
            director = r
            break
    if director is None:
        director = results[0]

    director_id = director.get("id")

    send_director_card(message.chat.id, message.from_user.id, director_id, searched_from="str")

    bot.delete_state(message.from_user.id, message.chat.id)
