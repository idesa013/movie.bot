from telebot.types import ReplyKeyboardMarkup, KeyboardButton


_TEXT = {
    "en": {
        "movie": "🎬 Movie Search",
        "actor": "🎭 Search Actor",
        "director": "🎬 Search Director",
        "favorites": "⭐ Favorites",
        "recommendations": "✨ Recommendations",
        "fav_movies": "🎬 Movies",
        "fav_actors": "🎭 Actors",
        "fav_directors": "🎬 Directors",
        "rec_new": "🆕 New Releases",
        "rec_genre": "🎭 By Genre",
        "rec_new_genre": "🆕🎭 New by Genre",
        "back": "⬅ Back",
    },
    "ru": {
        "movie": "🎬 Поиск фильма",
        "actor": "🎭 Поиск актёра",
        "director": "🎬 Поиск режиссёра",
        "favorites": "⭐ Избранное",
        "recommendations": "✨ Рекомендации",
        "fav_movies": "🎬 Фильмы",
        "fav_actors": "🎭 Актеры",
        "fav_directors": "🎬 Режиссеры",
        "rec_new": "🆕 Новинки",
        "rec_genre": "🎭 По жанру",
        "rec_new_genre": "🆕🎭 Новинки по жанру",
        "back": "⬅ Назад",
    },
}


def main_menu(lang: str = "en"):
    lang = lang if lang in _TEXT else "en"
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        KeyboardButton(_TEXT[lang]["movie"]),
        KeyboardButton(_TEXT[lang]["actor"]),
        KeyboardButton(_TEXT[lang]["director"]),
    )
    kb.row(
        KeyboardButton(_TEXT[lang]["favorites"]),
        KeyboardButton(_TEXT[lang]["recommendations"]),
    )
    return kb


def favorites_menu(lang: str = "en"):
    lang = lang if lang in _TEXT else "en"
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        KeyboardButton(_TEXT[lang]["fav_movies"]),
        KeyboardButton(_TEXT[lang]["fav_actors"]),
        KeyboardButton(_TEXT[lang]["fav_directors"]),
    )
    kb.row(KeyboardButton(_TEXT[lang]["back"]))
    return kb


def recommendations_menu(lang: str = "en"):
    lang = lang if lang in _TEXT else "en"
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        KeyboardButton(_TEXT[lang]["rec_new"]),
        KeyboardButton(_TEXT[lang]["rec_genre"]),

    )
    kb.row(
        KeyboardButton(_TEXT[lang]["rec_new_genre"]), 
        KeyboardButton(_TEXT[lang]["back"]),
    )
    return kb