from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from config_data.config import ADMIN_IDS
from keyboards.reply.main_menu import main_menu
from keyboards.reply.texts import MAIN_MENU_TEXT, ADMIN_MENU_TEXT


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def admin_main_menu(lang: str = "en"):
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
    kb.row(KeyboardButton(ADMIN_MENU_TEXT[lang]["admin_panel"]))
    return kb


def get_main_menu(user_id: int, lang: str = "en"):
    return admin_main_menu(lang) if is_admin(user_id) else main_menu(lang)


def admin_panel_menu(lang: str = "en"):
    lang = lang if lang in ADMIN_MENU_TEXT else "en"

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        KeyboardButton(ADMIN_MENU_TEXT[lang]["users"]),
        KeyboardButton(ADMIN_MENU_TEXT[lang]["messages"]),
        KeyboardButton(ADMIN_MENU_TEXT[lang]["back_to_menu"]),
    )
    kb.row(
        KeyboardButton(ADMIN_MENU_TEXT[lang]["search_user"]),
        KeyboardButton(ADMIN_MENU_TEXT[lang]["search_blocked"]),
    )
    return kb
