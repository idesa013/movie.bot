from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def _title_units(title: str) -> int:
    t = (title or "").strip()
    ln = len(t)
    if ln <= 14:
        return 1
    if ln <= 24:
        return 2
    return 3


def actor_movies_markup(movies: list) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()

    row = []
    used = 0

    def flush():
        nonlocal row, used
        if row:
            markup.row(*row)
            row = []
            used = 0

    for movie in movies:
        title = (movie.get("title") or "Movie").strip()
        movie_id = movie.get("id")
        if not movie_id:
            continue

        units = _title_units(title)
        btn = InlineKeyboardButton(
            text=title,
            callback_data=f"movie_{movie_id}_actor",
            style="primary",
        )

        if units >= 3:
            flush()
            markup.row(btn)
            continue

        if used + units > 3:
            flush()

        row.append(btn)
        used += units

    flush()
    return markup
