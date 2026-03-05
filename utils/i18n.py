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


def route_menu_or_command(bot, message) -> bool:
    """
    Использовать ВНУТРИ state-хендлеров (поиск фильма/актёра/режиссёра),
    чтобы текст кнопок меню и команды (/start, /help, /registration)
    НЕ воспринимались как поисковый запрос.
    Возвращает True, если сообщение было обработано здесь.
    """
    txt = (getattr(message, "text", "") or "").strip()
    if not txt:
        return False

    user_id = message.from_user.id
    chat_id = message.chat.id

    # 1) Команды
    if txt.startswith("/"):
        cmd = txt.split()[0].lower()

        # сбрасываем состояние, чтобы команды работали "как обычно"
        try:
            bot.delete_state(user_id, chat_id)
        except Exception:
            pass

        if cmd == "/start":
            # дергаем существующий handler /start
            from handlers.default_handlers.start import (
                bot_start,
            )  # локальный импорт без циклов на старте

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

        # неизвестную команду не глушим (пусть обработает echo/другие)
        return False

    # 2) Кнопки главного меню (reply keyboard)
    try:
        from keyboards.reply import main_menu as mm

        lang = get_user_language(user_id)

        # сравниваем с реальными текстами кнопок из main_menu.py
        movie_txt = mm._TEXT.get(lang, mm._TEXT["en"])["movie"]
        actor_txt = mm._TEXT.get(lang, mm._TEXT["en"])["actor"]
        director_txt = mm._TEXT.get(lang, mm._TEXT["en"])["director"]

        if txt == movie_txt:
            try:
                bot.delete_state(user_id, chat_id)
            except Exception:
                pass
            from handlers.custom_handlers.movie_start import start_movie_search

            start_movie_search(message)
            return True

        if txt == actor_txt:
            try:
                bot.delete_state(user_id, chat_id)
            except Exception:
                pass
            from handlers.custom_handlers.actor_search_start import start_actor_search

            start_actor_search(message)
            return True

        if txt == director_txt:
            try:
                bot.delete_state(user_id, chat_id)
            except Exception:
                pass
            from handlers.custom_handlers.director_search_start import (
                start_director_search,
            )

            start_director_search(message)
            return True

    except Exception:
        # если что-то пошло не так — просто не маршрутизируем
        return False

    return False
