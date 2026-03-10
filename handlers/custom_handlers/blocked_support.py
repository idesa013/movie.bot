from telebot.types import CallbackQuery, Message

from loader import bot
from states.support import SupportState
from database.user_messages import add_user_message
from utils.i18n import get_user_language
from utils.access import is_user_blocked


@bot.callback_query_handler(func=lambda c: c.data == "blocked_write_admin")
def blocked_write_admin(call: CallbackQuery):
    lang = get_user_language(call.from_user.id)
    bot.set_state(call.from_user.id, SupportState.waiting_for_message, call.message.chat.id)
    bot.send_message(
        call.message.chat.id,
        "Напишите сообщение администратору." if lang == "ru" else "Write your message to the administrator.",
    )
    bot.answer_callback_query(call.id)


@bot.message_handler(state=SupportState.waiting_for_message, content_types=["text"])
def save_blocked_user_message(message: Message):
    lang = get_user_language(message.from_user.id)

    if not is_user_blocked(message.from_user.id):
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(
            message.chat.id,
            "Вы больше не заблокированы." if lang == "ru" else "You are no longer blocked.",
        )
        return

    text = (message.text or "").strip()
    if not text:
        return

    add_user_message(
        user_id=message.from_user.id,
        username=message.from_user.username,
        user_msg=text,
    )

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(
        message.chat.id,
        "Сообщение отправлено администратору." if lang == "ru" else "Message sent to the administrator.",
    )
