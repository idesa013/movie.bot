from telebot.types import ReplyKeyboardMarkup, KeyboardButton


_TEXT = {
    "en": "📱 Send contact",
    "ru": "📱 Отправить контакт",
}


def request_contact(lang: str = "en") -> ReplyKeyboardMarkup:
    lang = lang if lang in _TEXT else "en"

    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton(text=_TEXT[lang], request_contact=True))
    return kb