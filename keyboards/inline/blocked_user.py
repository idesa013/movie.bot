from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def blocked_user_markup(lang: str = "en"):
    markup = InlineKeyboardMarkup()
    text = "✉ Написать администратору" if lang == "ru" else "✉ Write to Administrator"
    markup.add(
        InlineKeyboardButton(
            text=text,
            callback_data="blocked_write_admin",
            style="primary",
        )
    )
    return markup
