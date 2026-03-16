from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_language_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton(text="English", callback_data="set_lang:en"),
        InlineKeyboardButton(text="Русский", callback_data="set_lang:ru"),
    )

    return keyboard
