from telebot.types import Message
from loader import bot
from states.actor import ActorSearchState
from api.tmdb_actor import search_actor
from utils.person_service import send_actor_card


@bot.message_handler(state=ActorSearchState.waiting_for_actor_name)
def process_actor_search(message: Message):
    query = message.text

    data = search_actor(query)
    results = data.get("results")
    if not results:
        bot.send_message(message.chat.id, "Actor not found")
        return

    actor = results[0]
    actor_id = actor.get("id")

    send_actor_card(message.chat.id, message.from_user.id, actor_id, searched_from="str")

    bot.delete_state(message.from_user.id, message.chat.id)
