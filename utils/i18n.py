from __future__ import annotations

from database.models import User
from utils.access import ensure_user_not_blocked


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
    "choose_section": {"en": "Choose section:", "ru": "Выберите раздел:"},
    "need_registration": {
        "en": "❗ You need to complete registration to use the bot.",
        "ru": "❗ Чтобы пользоваться ботом, нужно пройти регистрацию.",
    },
    "start_registration": {"en": "Start registration", "ru": "Начать регистрацию"},
    "movie_not_found": {"en": "Movie not found", "ru": "Фильм не найден"},
    "movie_not_found_retry": {
        "en": "Movie not found. Try another title or press 'Menu'.",
        "ru": "Фильм не найден. Попробуйте ввести другое название или нажмите «Меню».",
    },
    "actor_not_found": {"en": "Actor not found", "ru": "Актёр не найден"},
    "actor_not_found_retry": {
        "en": "Actor not found. Try again or press 'Menu'.",
        "ru": "Актёр не найден. Попробуйте ещё раз или нажмите «Меню».",
    },
    "director_not_found": {"en": "Director not found", "ru": "Режиссёр не найден"},
    "director_not_found_retry": {
        "en": "Director not found. Try again or press 'Menu'.",
        "ru": "Режиссёр не найден. Попробуйте ещё раз или нажмите «Меню».",
    },
    "enter_movie_title": {
        "en": "Enter the movie title:",
        "ru": "Введите название фильма:",
    },
    "enter_actor_name": {
        "en": "Enter the actor name:",
        "ru": "Введите имя актёра:",
    },
    "enter_director_name": {
        "en": "Enter the director name:",
        "ru": "Введите имя режиссёра:",
    },
    "recommendations_empty": {
        "en": "Add movies to Favorites first to get recommendations.",
        "ru": "Сначала добавьте фильмы в избранное, чтобы получить рекомендации.",
    },
    "new_releases_title": {
        "en": "New releases:",
        "ru": "Новинки:",
    },
    "recommendations_by_genre_title": {
        "en": "✨ Recommended movies by genre: {genre_name}",
        "ru": "✨ Рекомендуемые фильмы по жанру: {genre_name}",
    },
    "new_by_genre_title": {
        "en": "New by genre: {genre_name}",
        "ru": "Новинки по жанру: {genre_name}",
    },
    "actor_recommendations_empty": {
        "en": "Add actors to Favorites first to get actor recommendations.",
        "ru": "Сначала добавьте актеров в избранное, чтобы получить рекомендации.",
    },
    "director_recommendations_empty": {
        "en": "Add directors to Favorites first to get director recommendations.",
        "ru": "Сначала добавьте режиссеров в избранное, чтобы получить рекомендации.",
    },
    "actor_recommendations_title": {
        "en": "Favorite actors:",
        "ru": "Любимые актеры:",
    },
    "director_recommendations_title": {
        "en": "Favorite directors:",
        "ru": "Любимые режиссеры:",
    },
    "fav_added": {"en": "Added: {name}", "ru": "Добавлено: {name}"},
    "fav_removed": {"en": "Removed: {name}", "ru": "Удалено: {name}"},
}


def t(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in (LANG_EN, LANG_RU) else LANG_EN
    text = TEXT.get(key, {}).get(lang, key)
    return text.format(**kwargs) if kwargs else text


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


def is_registered(user_id: int) -> bool:
    user = User.get_or_none(User.user_id == user_id)
    if not user:
        return False
    return bool((user.email or "").strip()) and bool((user.phone_number or "").strip())


def ensure_registered(bot, chat_id: int, user_id: int) -> bool:
    if not ensure_user_not_blocked(bot, chat_id, user_id):
        return False

    if is_registered(user_id):
        return True

    lang = get_user_language(user_id)

    from keyboards.inline.registration import get_registration_required_keyboard

    bot.send_message(
        chat_id,
        t(lang, "need_registration"),
        reply_markup=get_registration_required_keyboard(lang),
    )
    return False
