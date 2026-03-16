from telebot.types import Message

from loader import bot
from states.actor import ActorSearchState
from utils.i18n import get_user_language, ensure_registered, t
from utils.access import ensure_user_not_blocked
from keyboards.reply.texts import MAIN_MENU_TEXT


@bot.message_handler(
    func=lambda m: m.text
    in (MAIN_MENU_TEXT["en"]["actor"], MAIN_MENU_TEXT["ru"]["actor"])
)
def start_actor_search(message: Message):
    if not ensure_user_not_blocked(bot, message.chat.id, message.from_user.id):
        return

    if not ensure_registered(bot, message.chat.id, message.from_user.id):
        return

    lang = get_user_language(message.from_user.id)
    bot.set_state(
        message.from_user.id, ActorSearchState.waiting_for_actor_name, message.chat.id
    )
    bot.send_message(message.chat.id, t(lang, "enter_actor_name"))
