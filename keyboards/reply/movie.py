from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def movie_button():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🎬 Movie Search"))
    return kb
