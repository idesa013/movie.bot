from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def movie_actors_markup(actors: list) -> InlineKeyboardMarkup:
    """actors: list of dicts from TMDB credits cast with keys id, name"""
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for a in actors:
        name = a.get("name") or "Actor"
        a_id = a.get("id")
        if a_id is None:
            continue
        buttons.append(InlineKeyboardButton(text=name, callback_data=f"actor_{a_id}"))
    if buttons:
        markup.add(*buttons)
    return markup
