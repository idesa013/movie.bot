from __future__ import annotations

from database.models import User

LANG_EN = "en"
LANG_RU = "ru"

TMDB_LANG = {
    LANG_EN: "en-US",
    LANG_RU: "ru-RU",
}

TEXT = {
    "choose_language": {"en": "Choose language:", "ru": "Выберите язык:"},
    "language_saved": {"en": "✅ Language saved.", "ru": "✅ Язык сохранён."},
    "choose_action": {"en": "Choose an action:", "ru": "Выберите действие:"},
    "movie_not_found": {"en": "Movie not found", "ru": "Фильм не найден"},
    "actor_not_found": {"en": "Actor not found", "ru": "Актёр не найден"},
    "director_not_found": {"en": "Director not found", "ru": "Режиссёр не найден"},
    "no_ru_info_fallback": {
        "en": "No English information. Russian shown below:",
        "ru": "На русском языке этой информации нет, есть на английском:",
    },
    "no_bio": {"en": "No biography available", "ru": "Биография отсутствует"},
    "no_overview": {"en": "No description available", "ru": "Описание отсутствует"},
    "known_movies": {"en": "🎬 Known for:", "ru": "🎬 Известные фильмы:"},
    "directed_movies": {"en": "🎥 Directed:", "ru": "🎥 Фильмы (как режиссёр):"},
    "birthday": {"en": "📅 Birthday:", "ru": "📅 Дата рождения:"},
    "place_of_birth": {"en": "🌍 Place of birth:", "ru": "🌍 Место рождения:"},
    "movies": {"en": "🎬 Movies:", "ru": "🎬 Фильмы:"},
    "directors": {"en": "🎬 Directors:", "ru": "🎬 Режиссёры:"},
    "actors": {"en": "👥 Actors:", "ru": "👥 Актёры:"},
    "release_date": {"en": "📅 Release Date:", "ru": "📅 Дата выхода:"},
    "rating": {"en": "⭐ Rating:", "ru": "⭐ Рейтинг:"},
    "genres": {"en": "🎭 Genres:", "ru": "🎭 Жанры:"},
    "fav_added": {
        "en": "{name} added to Favorites",
        "ru": "{name} добавлен(а) в избранное",
    },
    "fav_removed": {
        "en": "{name} removed from Favorites",
        "ru": "{name} удален(а) из избранного",
    },
}


def t(lang: str, key: str) -> str:
    lang = lang if lang in (LANG_EN, LANG_RU) else LANG_EN
    return TEXT.get(key, {}).get(lang, key)


def get_user_language(user_id: int) -> str:
    try:
        user = User.get_or_none(User.user_id == user_id)
        if user and getattr(user, "language", None) in (LANG_EN, LANG_RU):
            return user.language
    except Exception:
        pass
    return LANG_EN


def tmdb_language(user_lang: str) -> str:
    return TMDB_LANG.get(user_lang, "en-US")
