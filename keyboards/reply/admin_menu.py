from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from config_data.config import ADMIN_ID
from keyboards.reply.main_menu import main_menu, _TEXT as MAIN_TEXT


_TEXT = {
    "en": {
        "admin_panel": "🛠 Admin Panel",
        "users": "👥 Users",
        "back": "⬅ Back",
        "admin_choose": "Choose an action:",
        "users_title": "👥 Users",
    },
    "ru": {
        "admin_panel": "🛠 Админ панель",
        "users": "👥 Пользователи",
        "back": "⬅ Назад",
        "admin_choose": "Выберите действие:",
        "users_title": "👥 Пользователи",
    },
}


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def admin_main_menu(lang: str = "en"):
    """
    Главное меню для администратора:
    стандартное меню + кнопка входа в админку.
    """
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
    kb.row(
        KeyboardButton(_TEXT[lang]["admin_panel"]),
    )
    return kb


def get_main_menu(user_id: int, lang: str = "en"):
    """
    Возвращает обычное меню или меню администратора.
    """
    if is_admin(user_id):
        return admin_main_menu(lang)
    return main_menu(lang)


def admin_panel_menu(lang: str = "en"):
    lang = lang if lang in _TEXT else "en"

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton(_TEXT[lang]["users"]))
    kb.row(KeyboardButton(_TEXT[lang]["back"]))
    return kb