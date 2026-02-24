from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def actor_button():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🎭 Search Actor"))
    return kb
