from __future__ import annotations

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

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
    "need_registration": {
        "en": "❗ You need to complete registration to use the bot.",
        "ru": "❗ Чтобы пользоваться ботом, нужно пройти регистрацию.",
    },
    "start_registration": {"en": "Start registration", "ru": "Начать регистрацию"},
    "recommendations_empty": {
        "en": "Add movies to Favorites first to get recommendations.",
        "ru": "Сначала добавьте фильмы в избранное, чтобы получить рекомендации.",
    },
    "recommendations_title": {
        "en": "✨ Recommended movies based on your favorite genre:",
        "ru": "✨ Рекомендуемые фильмы на основе вашего любимого жанра:",
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

    if txt.startswith("/"):
        cmd = txt.split()[0].lower()

        try:
            bot.delete_state(user_id, chat_id)
        except Exception:
            pass

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

    try:
        from keyboards.reply import main_menu as mm

        lang = get_user_language(user_id)
        pack = mm._TEXT.get(lang, mm._TEXT["en"])

        if txt == pack["movie"]:
            try:
                bot.delete_state(user_id, chat_id)
            except Exception:
                pass
            from handlers.custom_handlers.movie_start import start_movie_search
            start_movie_search(message)
            return True

        if txt == pack["actor"]:
            try:
                bot.delete_state(user_id, chat_id)
            except Exception:
                pass
            from handlers.custom_handlers.actor_search_start import start_actor_search
            start_actor_search(message)
            return True

        if txt == pack["director"]:
            try:
                bot.delete_state(user_id, chat_id)
            except Exception:
                pass
            from handlers.custom_handlers.director_search_start import start_director_search
            start_director_search(message)
            return True

        if txt == pack["recommend_genre"]:
            try:
                bot.delete_state(user_id, chat_id)
            except Exception:
                pass
            from handlers.custom_handlers.movie_start import show_recommendations
            show_recommendations(message)
            return True

        if txt == pack["recommend_actor"]:
            try:
                bot.delete_state(user_id, chat_id)
            except Exception:
                pass
            from handlers.custom_handlers.movie_start import show_actor_recommendations
            show_actor_recommendations(message)
            return True

        if txt == pack["recommend_director"]:
            try:
                bot.delete_state(user_id, chat_id)
            except Exception:
                pass
            from handlers.custom_handlers.movie_start import show_director_recommendations
            show_director_recommendations(message)
            return True

    except Exception:
        return False

    return False