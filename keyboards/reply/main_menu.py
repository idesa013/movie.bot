from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("🎬 Movie Search"),
        KeyboardButton("🎭 Search Actor"),
        KeyboardButton("🎬 Search Director"),
    )
    return kb
