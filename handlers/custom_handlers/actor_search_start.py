from telebot.types import Message

from loader import bot
from states.actor import ActorSearchState
from utils.i18n import get_user_language


@bot.message_handler(func=lambda m: m.text in ("🎭 Search Actor", "🎭 Поиск актёра"))
def start_actor_search(message: Message):
    lang = get_user_language(message.from_user.id)

    bot.set_state(message.from_user.id, ActorSearchState.waiting_for_actor_name, message.chat.id)

    if lang == "ru":
        bot.send_message(message.chat.id, "Введите имя актёра:")
    else:
        bot.send_message(message.chat.id, "Enter the actor name:")
