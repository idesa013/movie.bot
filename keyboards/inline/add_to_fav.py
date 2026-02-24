from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def add_favorites_button(movie_id: int, in_favorites: bool = False):
    markup = InlineKeyboardMarkup()

    if in_favorites:
        button = InlineKeyboardButton(
            text="Remove from Favorites",
            callback_data=f"remove_fav:{movie_id}",
            style="danger",
        )
    else:
        button = InlineKeyboardButton(
            text="Add to Favorites",
            callback_data=f"add_fav:{movie_id}",
            style="success",
        )

    markup.add(button)
    return markup
