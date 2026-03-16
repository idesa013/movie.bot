from telebot.types import Message

from loader import bot
from utils.i18n import get_user_language
from utils.access import ensure_user_not_blocked
from utils.menu_router import route_menu_or_command


def _has_state(message: Message) -> bool:
    state = bot.get_state(message.from_user.id, message.chat.id)
    return bool(state)


@bot.message_handler(func=lambda m: not _has_state(m), content_types=["text"])
def echo(message: Message):
    if not ensure_user_not_blocked(bot, message.chat.id, message.from_user.id):
        return

    if route_menu_or_command(bot, message):
        return

    lang = get_user_language(message.from_user.id)
    bot.send_message(
        message.chat.id,
        (
            "Эхо без состояния или фильтра.\nСообщение: "
            if lang == "ru"
            else "Echo (no state/filter).\nMessage: "
        )
        + (message.text or ""),
    )
