from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("🎬 Movie Search"),
        KeyboardButton("🎭 Search Actor"),
    )
    return kb
