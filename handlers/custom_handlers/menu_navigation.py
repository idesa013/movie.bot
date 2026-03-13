from telebot.types import Message

from loader import bot
from keyboards.reply.main_menu import favorites_menu, recommendations_menu, _TEXT
from keyboards.reply.admin_menu import get_main_menu
from utils.i18n import get_user_language, ensure_registered, t


@bot.message_handler(
    func=lambda m: (m.text or "").strip()
    in (_TEXT["en"]["favorites"], _TEXT["ru"]["favorites"])
)
def open_favorites_menu(message: Message):
    if not ensure_registered(bot, message.chat.id, message.from_user.id):
        return

    lang = get_user_language(message.from_user.id)
    bot.send_message(
        message.chat.id,
        t(lang, "choose_section"),
        reply_markup=favorites_menu(lang),
    )


@bot.message_handler(
    func=lambda m: (m.text or "").strip()
    in (_TEXT["en"]["recommendations"], _TEXT["ru"]["recommendations"])
)
def open_recommendations_menu(message: Message):
    if not ensure_registered(bot, message.chat.id, message.from_user.id):
        return

    lang = get_user_language(message.from_user.id)
    bot.send_message(
        message.chat.id,
        t(lang, "choose_section"),
        reply_markup=recommendations_menu(lang),
    )


@bot.message_handler(
    func=lambda m: (m.text or "").strip() in (_TEXT["en"]["back"], _TEXT["ru"]["back"])
)
def back_to_main_menu(message: Message):
    if not ensure_registered(bot, message.chat.id, message.from_user.id):
        return

    lang = get_user_language(message.from_user.id)
    bot.send_message(
        message.chat.id,
        t(lang, "choose_action"),
        reply_markup=get_main_menu(message.from_user.id, lang),
    )
