from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def director_movies_markup(movies: list) -> InlineKeyboardMarkup:
    """
    Кнопки фильмов режиссёра.
    При переходе из карточки режиссёра используем источник 'dir' (для searched_from фильма).
    """
    markup = InlineKeyboardMarkup(row_width=2)

    buttons = []
    for movie in movies:
        title = movie.get("title", "Movie")
        movie_id = movie.get("id")
        buttons.append(
            InlineKeyboardButton(
                text=title,
                callback_data=f"movie_{movie_id}_dir",
            )
        )

    markup.add(*buttons)
    return markup
