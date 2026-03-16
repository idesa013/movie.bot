import importlib
from utils.i18n import get_user_language, LANG_EN


def load_handler(module_path, func_name):
    module = importlib.import_module(module_path)
    return getattr(module, func_name)


def route_menu_or_command(bot, message) -> bool:
    txt = (getattr(message, "text", "") or "").strip()
    if not txt:
        return False

    user_id = message.from_user.id
    chat_id = message.chat.id

    def clear_state():
        try:
            bot.delete_state(user_id, chat_id)
        except Exception:
            pass

    # команды
    if txt.startswith("/"):
        cmd = txt.split()[0].lower()
        clear_state()

        commands = {
            "/start": ("handlers.default_handlers.start", "bot_start"),
            "/help": ("handlers.default_handlers.help", "bot_help"),
            "/registration": ("handlers.custom_handlers.registration", "registration"),
        }

        target = commands.get(cmd)
        if not target:
            return False

        module, func = target
        handler = getattr(__import__(module, fromlist=[func]), func)
        handler(message)
        return True

    lang = get_user_language(user_id)

    try:
        from keyboards.reply.texts import MAIN_MENU_TEXT, ADMIN_MENU_TEXT

        main_pack = MAIN_MENU_TEXT.get(lang, MAIN_MENU_TEXT[LANG_EN])
        admin_pack = ADMIN_MENU_TEXT.get(lang, ADMIN_MENU_TEXT[LANG_EN])

        # импортируем обработчики
        from handlers.custom_handlers.movie_start import (
            start_movie_search,
            show_new_recommendations,
            show_recommendations,
            show_new_genre_recommendations,
        )

        from handlers.custom_handlers.actor_search_start import start_actor_search
        from handlers.custom_handlers.director_search_start import start_director_search

        from handlers.custom_handlers.menu_navigation import (
            open_favorites_menu,
            open_recommendations_menu,
            back_to_main_menu,
        )

        from handlers.custom_handlers.favorites_view import (
            show_favorite_movies,
            show_favorite_actors,
            show_favorite_directors,
        )

        from handlers.custom_handlers.admin_panel import (
            open_admin_panel,
            show_users_list,
            open_blocked_messages_users,
            admin_search_user,
            admin_search_blocked_user,
            admin_back_to_main_menu,
        )

        routes = {
            # основное меню
            main_pack["movie"]: (
                "handlers.custom_handlers.movie_start",
                "start_movie_search",
            ),
            main_pack["actor"]: (
                "handlers.custom_handlers.actor_search_start",
                "start_actor_search",
            ),
            main_pack["director"]: (
                "handlers.custom_handlers.director_search_start",
                "start_director_search",
            ),
            main_pack["favorites"]: (
                "handlers.custom_handlers.menu_navigation",
                "open_favorites_menu",
            ),
            main_pack["recommendations"]: (
                "handlers.custom_handlers.menu_navigation",
                "open_recommendations_menu",
            ),
            main_pack["fav_movies"]: (
                "handlers.custom_handlers.favorites_view",
                "show_favorite_movies",
            ),
            main_pack["fav_actors"]: (
                "handlers.custom_handlers.favorites_view",
                "show_favorite_actors",
            ),
            main_pack["fav_directors"]: (
                "handlers.custom_handlers.favorites_view",
                "show_favorite_directors",
            ),
            main_pack["rec_new"]: (
                "handlers.custom_handlers.movie_start",
                "show_new_recommendations",
            ),
            main_pack["rec_genre"]: (
                "handlers.custom_handlers.movie_start",
                "show_recommendations",
            ),
            main_pack["rec_new_genre"]: (
                "handlers.custom_handlers.movie_start",
                "show_new_genre_recommendations",
            ),
            main_pack["back"]: (
                "handlers.custom_handlers.menu_navigation",
                "back_to_main_menu",
            ),
            # админ
            admin_pack["admin_panel"]: (
                "handlers.custom_handlers.admin_panel",
                "open_admin_panel",
            ),
            admin_pack["users"]: (
                "handlers.custom_handlers.admin_panel",
                "show_users_list",
            ),
            admin_pack["messages"]: (
                "handlers.custom_handlers.admin_panel",
                "open_blocked_messages_users",
            ),
            admin_pack["search_user"]: (
                "handlers.custom_handlers.admin_panel",
                "admin_search_user",
            ),
            admin_pack["search_blocked"]: (
                "handlers.custom_handlers.admin_panel",
                "admin_search_blocked_user",
            ),
            admin_pack["back_to_menu"]: (
                "handlers.custom_handlers.admin_panel",
                "admin_back_to_main_menu",
            ),
        }

        target = routes.get(txt)

        if target:
            clear_state()

            module, func = target
            handler = load_handler(module, func)

            handler(message)
            return True

    except Exception:
        return False

    return False
