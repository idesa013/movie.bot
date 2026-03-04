from telebot.types import ReplyKeyboardMarkup, KeyboardButton


_TEXT = {
    "en": {
        "movie": "🎬 Movie Search",
        "actor": "🎭 Search Actor",
        "director": "🎬 Search Director",
    },
    "ru": {
        "movie": "🎬 Поиск фильма",
        "actor": "🎭 Поиск актёра",
        "director": "🎬 Поиск режиссёра",
    },
}


def main_menu(lang: str = "en"):
    lang = lang if lang in _TEXT else "en"
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton(_TEXT[lang]["movie"]),
        KeyboardButton(_TEXT[lang]["actor"]),
        KeyboardButton(_TEXT[lang]["director"]),
    )
    return kb
