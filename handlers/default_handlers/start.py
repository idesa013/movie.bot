from datetime import datetime

from telebot.types import Message, CallbackQuery

from keyboards.inline.language import get_language_keyboard
from keyboards.reply.admin_menu import get_main_menu
from loader import bot
from database.models import User
from utils.i18n import t, LANG_EN, LANG_RU, ensure_registered
from utils.set_bot_commands import set_chat_commands


def _ensure_user_row(user_id: int, username: str | None, language: str) -> None:
    user = User.get_or_none(User.user_id == user_id)

    if user is None:
        User.create(
            user_id=user_id,
            username=username,
            name="",
            surname="",
            age=0,
            email="",
            phone_number="",
            reg_date=datetime.now(),
            language=language,
            active=True,
        )
    else:
        changed = False

        if username and user.username != username:
            user.username = username
            changed = True

        if getattr(user, "language", None) != language:
            user.language = language
            changed = True

        if getattr(user, "active", None) is None:
            user.active = True
            changed = True

        if changed:
            user.save()


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    bot.send_message(
        message.chat.id,
        f"{t(LANG_EN, 'choose_language')} / {t(LANG_RU, 'choose_language')}",
        reply_markup=get_language_keyboard(),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("set_lang:"))
def set_language(call: CallbackQuery):
    lang = call.data.split(":", 1)[1]

    if lang not in (LANG_EN, LANG_RU):
        bot.answer_callback_query(call.id, "Unknown language")
        return

    _ensure_user_row(call.from_user.id, call.from_user.username, lang)
    set_chat_commands(bot, call.message.chat.id, lang)

    bot.edit_message_text(
        t(lang, "language_saved"),
        call.message.chat.id,
        call.message.message_id,
    )

    if not ensure_registered(bot, call.message.chat.id, call.from_user.id):
        bot.answer_callback_query(call.id)
        return

    bot.send_message(
        call.message.chat.id,
        t(lang, "choose_action"),
        reply_markup=get_main_menu(call.from_user.id, lang),
    )
    bot.answer_callback_query(call.id)
