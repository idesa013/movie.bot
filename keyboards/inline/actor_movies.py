from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def actor_movies_markup(movies: list) -> InlineKeyboardMarkup:
    """
    Формирует InlineKeyboardMarkup для списка фильмов актёра
    movies: список словарей с ключами 'title' и 'id'
    Кнопки располагаются в 2 колонки
    """
    markup = InlineKeyboardMarkup(row_width=2)

    buttons = []
    for movie in movies:
        title = movie.get("title", "Movie")
        movie_id = movie.get("id")
        buttons.append(
            InlineKeyboardButton(
                text=title, callback_data=f"movie_{movie_id}", style="primary"
            )
        )

    # Добавляем кнопки по 2 в ряд
    markup.add(*buttons)

    return markup
