from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def movie_directors_markup(directors: list) -> InlineKeyboardMarkup:
    """directors: list of dicts from TMDB credits crew with keys id, name"""
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for d in directors:
        name = d.get("name") or "Director"
        d_id = d.get("id")
        if d_id is None:
            continue
        buttons.append(InlineKeyboardButton(text=name, callback_data=f"director_{d_id}"))
    if buttons:
        markup.add(*buttons)
    return markup
