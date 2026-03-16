from utils.i18n import get_user_language, LANG_EN


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
        from keyboards.reply.texts import MAIN_MENU_TEXT, ADMIN_MENU_TEXT

        main_pack = MAIN_MENU_TEXT.get(lang, MAIN_MENU_TEXT[LANG_EN])
        admin_pack = ADMIN_MENU_TEXT.get(lang, ADMIN_MENU_TEXT[LANG_EN])

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
