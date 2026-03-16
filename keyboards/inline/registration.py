from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.i18n import t


def get_registration_required_keyboard(lang: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            text=t(lang, "start_registration"),
            callback_data="start_registration",
        )
    )

    return keyboard
