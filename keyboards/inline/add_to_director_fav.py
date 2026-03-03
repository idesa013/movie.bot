from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def add_director_favorites_button(director_id: int, in_favorites: bool = False):
    markup = InlineKeyboardMarkup()

    if in_favorites:
        button = InlineKeyboardButton(
            text="Remove from Favorites",
            callback_data=f"remove_director_fav:{director_id}",
            style="danger",
        )
    else:
        button = InlineKeyboardButton(
            text="Add to Favorites",
            callback_data=f"add_director_fav:{director_id}",
            style="success",
        )

    markup.add(button)
    return markup
