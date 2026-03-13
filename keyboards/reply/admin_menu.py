from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from config_data.config import ADMIN_IDS
from keyboards.reply.main_menu import main_menu, _TEXT as MAIN_TEXT


_TEXT = {
    "en": {
        "admin_panel": "🛠 Admin Panel",
        "users": "👥 Users",
        "messages": "✉ Messages",
        "search_user": "🔎 Find User",
        "search_blocked": "⛔🔎 Find Blocked",
        "back_to_menu": "⬅ Back to Menu",
    },
    "ru": {
        "admin_panel": "🛠 Админ панель",
        "users": "👥 Пользователи",
        "messages": "✉ Сообщения",
        "search_user": "🔎 Найти пользователя",
        "search_blocked": "⛔🔎 Найти заблокированного",
        "back_to_menu": "⬅ Назад в меню",
    },
}


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def admin_main_menu(lang: str = "en"):
    lang = lang if lang in MAIN_TEXT else "en"

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        KeyboardButton(MAIN_TEXT[lang]["movie"]),
        KeyboardButton(MAIN_TEXT[lang]["actor"]),
        KeyboardButton(MAIN_TEXT[lang]["director"]),
    )
    kb.row(
        KeyboardButton(MAIN_TEXT[lang]["favorites"]),
        KeyboardButton(MAIN_TEXT[lang]["recommendations"]),
    )
    kb.row(KeyboardButton(_TEXT[lang]["admin_panel"]))
    return kb


def get_main_menu(user_id: int, lang: str = "en"):
    return admin_main_menu(lang) if is_admin(user_id) else main_menu(lang)


def admin_panel_menu(lang: str = "en"):
    lang = lang if lang in _TEXT else "en"

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        KeyboardButton(_TEXT[lang]["users"]),
        KeyboardButton(_TEXT[lang]["messages"]),
        KeyboardButton(_TEXT[lang]["back_to_menu"]),
    )
    kb.row(
        KeyboardButton(_TEXT[lang]["search_user"]),
        KeyboardButton(_TEXT[lang]["search_blocked"]),
    )
    return kb
