from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


_TEXT = {
    "en": {"add": "Add to Favorites", "remove": "Remove from Favorites"},
    "ru": {"add": "Добавить в избранное", "remove": "Удалить из избранного"},
}


def add_director_favorites_button(director_id: int, in_favorites: bool = False, lang: str = "en"):
    markup = InlineKeyboardMarkup()
    lang = lang if lang in _TEXT else "en"

    if in_favorites:
        button = InlineKeyboardButton(
            text=_TEXT[lang]["remove"],
            callback_data=f"remove_director_fav:{director_id}",
            style="danger",
        )
    else:
        button = InlineKeyboardButton(
            text=_TEXT[lang]["add"],
            callback_data=f"add_director_fav:{director_id}",
            style="success",
        )

    markup.add(button)
    return markup
