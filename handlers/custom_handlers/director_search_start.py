from telebot.types import Message

from loader import bot
from states.director import DirectorSearchState
from utils.i18n import get_user_language, ensure_registered
from utils.access import ensure_user_not_blocked


@bot.message_handler(func=lambda m: m.text in ("🎬 Search Director", "🎬 Поиск режиссёра"))
def start_director_search(message: Message):
    if not ensure_user_not_blocked(bot, message.chat.id, message.from_user.id):
        return

    if not ensure_registered(bot, message.chat.id, message.from_user.id):
        return

    lang = get_user_language(message.from_user.id)
    bot.set_state(message.from_user.id, DirectorSearchState.waiting_for_director_name, message.chat.id)

    bot.send_message(message.chat.id, "Введите имя режиссёра:" if lang == "ru" else "Enter the director name:")