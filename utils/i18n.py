from __future__ import annotations

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

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
        "en": "🆕 New releases:",
        "ru": "🆕 Новинки:",
    },
    "recommendations_by_genre_title": {
        "en": "✨ Recommended movies by genre: <b>{genre_name}</b>",
        "ru": "✨ Рекомендуемые фильмы по жанру: <b>{genre_name}</b>",
    },
    "new_by_genre_title": {
        "en": "🆕🎭 New by genre: <b>{genre_name}</b>",
        "ru": "🆕🎭 Новинки по жанру: <b>{genre_name}</b>",
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
        "en": "🎭 Favorite actors:",
        "ru": "🎭 Любимые актеры:",
    },
    "director_recommendations_title": {
        "en": "🎬 Favorite directors:",
        "ru": "🎬 Любимые режиссеры:",
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


def registration_required_markup(lang: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text=t(lang, "start_registration"),
            callback_data="start_registration",
            style="primary",
        )
    )
    return markup


def ensure_registered(bot, chat_id: int, user_id: int) -> bool:
    if not ensure_user_not_blocked(bot, chat_id, user_id):
        return False

    if is_registered(user_id):
        return True

    lang = get_user_language(user_id)
    bot.send_message(
        chat_id,
        t(lang, "need_registration"),
        reply_markup=registration_required_markup(lang),
    )
    return False


def route_menu_or_command(bot, message) -> bool:
    txt = (getattr(message, "text", "") or "").strip()
    if not txt:
        return False

    user_id = message.from_user.id
    chat_id = message.chat.id

    def _clear_state():
        try:
            bot.delete_state(user_id, chat_id)
        except Exception:
            pass

    if txt.startswith("/"):
        cmd = txt.split()[0].lower()
        _clear_state()

        if cmd == "/start":
            from handlers.default_handlers.start import bot_start

            bot_start(message)
            return True

        if cmd == "/help":
            from handlers.default_handlers.help import bot_help

            bot_help(message)
            return True

        if cmd == "/registration":
            from handlers.custom_handlers.registration import registration

            registration(message)
            return True

        return False

    lang = get_user_language(user_id)

    try:
        from keyboards.reply.main_menu import _TEXT as main_text
        from keyboards.reply.admin_menu import _TEXT as admin_text

        main_pack = main_text.get(lang, main_text[LANG_EN])
        admin_pack = admin_text.get(lang, admin_text[LANG_EN])

        if txt == main_pack["movie"]:
            _clear_state()
            from handlers.custom_handlers.movie_start import start_movie_search

            start_movie_search(message)
            return True

        if txt == main_pack["actor"]:
            _clear_state()
            from handlers.custom_handlers.actor_search_start import start_actor_search

            start_actor_search(message)
            return True

        if txt == main_pack["director"]:
            _clear_state()
            from handlers.custom_handlers.director_search_start import (
                start_director_search,
            )

            start_director_search(message)
            return True

        if txt == main_pack["favorites"]:
            _clear_state()
            from handlers.custom_handlers.menu_navigation import open_favorites_menu

            open_favorites_menu(message)
            return True

        if txt == main_pack["recommendations"]:
            _clear_state()
            from handlers.custom_handlers.menu_navigation import (
                open_recommendations_menu,
            )

            open_recommendations_menu(message)
            return True

        if txt == main_pack["fav_movies"]:
            _clear_state()
            from handlers.custom_handlers.favorites_view import show_favorite_movies

            show_favorite_movies(message)
            return True

        if txt == main_pack["fav_actors"]:
            _clear_state()
            from handlers.custom_handlers.favorites_view import show_favorite_actors

            show_favorite_actors(message)
            return True

        if txt == main_pack["fav_directors"]:
            _clear_state()
            from handlers.custom_handlers.favorites_view import show_favorite_directors

            show_favorite_directors(message)
            return True

        if txt == main_pack["rec_new"]:
            _clear_state()
            from handlers.custom_handlers.movie_start import show_new_recommendations

            show_new_recommendations(message)
            return True

        if txt == main_pack["rec_genre"]:
            _clear_state()
            from handlers.custom_handlers.movie_start import show_recommendations

            show_recommendations(message)
            return True

        if txt == main_pack["rec_new_genre"]:
            _clear_state()
            from handlers.custom_handlers.movie_start import (
                show_new_genre_recommendations,
            )

            show_new_genre_recommendations(message)
            return True

        if txt == main_pack["back"]:
            _clear_state()
            from handlers.custom_handlers.menu_navigation import back_to_main_menu

            back_to_main_menu(message)
            return True

        if txt == admin_pack["admin_panel"]:
            _clear_state()
            from handlers.custom_handlers.admin_panel import open_admin_panel

            open_admin_panel(message)
            return True

        if txt == admin_pack["users"]:
            _clear_state()
            from handlers.custom_handlers.admin_panel import show_users_list

            show_users_list(message)
            return True

        if txt == admin_pack["messages"]:
            _clear_state()
            from handlers.custom_handlers.admin_panel import open_blocked_messages_users

            open_blocked_messages_users(message)
            return True

        if txt == admin_pack["search_user"]:
            _clear_state()
            from handlers.custom_handlers.admin_panel import admin_search_user

            admin_search_user(message)
            return True

        if txt == admin_pack["search_blocked"]:
            _clear_state()
            from handlers.custom_handlers.admin_panel import admin_search_blocked_user

            admin_search_blocked_user(message)
            return True

        if txt == admin_pack["back_to_menu"]:
            _clear_state()
            from handlers.custom_handlers.admin_panel import admin_back_to_main_menu

            admin_back_to_main_menu(message)
            return True

    except Exception:
        return False

    return False
