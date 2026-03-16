from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from keyboards.reply.texts import MAIN_MENU_TEXT


def main_menu(lang: str = "en"):
    lang = lang if lang in MAIN_MENU_TEXT else "en"
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        KeyboardButton(MAIN_MENU_TEXT[lang]["movie"]),
        KeyboardButton(MAIN_MENU_TEXT[lang]["actor"]),
        KeyboardButton(MAIN_MENU_TEXT[lang]["director"]),
    )
    kb.row(
        KeyboardButton(MAIN_MENU_TEXT[lang]["favorites"]),
        KeyboardButton(MAIN_MENU_TEXT[lang]["recommendations"]),
    )
    return kb


def favorites_menu(lang: str = "en"):
    lang = lang if lang in MAIN_MENU_TEXT else "en"
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        KeyboardButton(MAIN_MENU_TEXT[lang]["fav_movies"]),
        KeyboardButton(MAIN_MENU_TEXT[lang]["fav_actors"]),
        KeyboardButton(MAIN_MENU_TEXT[lang]["fav_directors"]),
    )
    kb.row(KeyboardButton(MAIN_MENU_TEXT[lang]["back"]))
    return kb


def recommendations_menu(lang: str = "en"):
    lang = lang if lang in MAIN_MENU_TEXT else "en"
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        KeyboardButton(MAIN_MENU_TEXT[lang]["rec_new"]),
        KeyboardButton(MAIN_MENU_TEXT[lang]["rec_genre"]),
    )
    kb.row(
        KeyboardButton(MAIN_MENU_TEXT[lang]["rec_new_genre"]),
        KeyboardButton(MAIN_MENU_TEXT[lang]["back"]),
    )
    return kb
