from telebot.types import Message
from loader import bot
from states.actor import ActorSearchState


@bot.message_handler(func=lambda m: m.text == "🎭 Search Actor")
def start_actor_search(message: Message):
    bot.set_state(
        message.from_user.id,
        ActorSearchState.waiting_for_actor_name,
        message.chat.id,
    )
    bot.send_message(message.chat.id, "Enter actor name:")
