from telebot.types import Message
from loader import bot
from states.director import DirectorSearchState


@bot.message_handler(func=lambda m: m.text == "🎬 Search Director")
def start_director_search(message: Message):
    bot.set_state(
        message.from_user.id,
        DirectorSearchState.waiting_for_director_name,
        message.chat.id,
    )
    bot.send_message(message.chat.id, "Enter director name:")
