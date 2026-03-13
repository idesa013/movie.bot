from telebot.types import Message

from loader import bot
from states.director import DirectorSearchState
from utils.i18n import get_user_language, ensure_registered, t
from utils.access import ensure_user_not_blocked
from keyboards.reply.main_menu import _TEXT


@bot.message_handler(
    func=lambda m: m.text in (_TEXT["en"]["director"], _TEXT["ru"]["director"])
)
def start_director_search(message: Message):
    if not ensure_user_not_blocked(bot, message.chat.id, message.from_user.id):
        return

    if not ensure_registered(bot, message.chat.id, message.from_user.id):
        return

    lang = get_user_language(message.from_user.id)
    bot.set_state(
        message.from_user.id,
        DirectorSearchState.waiting_for_director_name,
        message.chat.id,
    )
    bot.send_message(message.chat.id, t(lang, "enter_director_name"))
