from loader import bot
from utils.movie_service import send_movie_card
from utils.i18n import ensure_registered
from utils.admin_context import resolve_effective_user_id


@bot.callback_query_handler(func=lambda c: c.data.startswith("movie_recom:"))
def movie_recom_callback(call):
    if not ensure_registered(bot, call.message.chat.id, call.from_user.id):
        bot.answer_callback_query(call.id)
        return

    movie_id = int(call.data.split(":")[1])
    effective_user_id = resolve_effective_user_id(call.from_user.id)

    send_movie_card(
        call.message.chat.id,
        movie_id,
        effective_user_id,
        searched_from="movie_recom",
        viewer_id=call.from_user.id,
    )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("movie_"))
def movie_callback(call):
    if not ensure_registered(bot, call.message.chat.id, call.from_user.id):
        bot.answer_callback_query(call.id)
        return

    parts = call.data.split("_")
    movie_id = int(parts[1])
    effective_user_id = resolve_effective_user_id(call.from_user.id)

    searched_from = "movie"
    if len(parts) >= 3:
        src = "_".join(parts[2:])
        mapping = {
            "str": "movie",
            "straight": "movie",
            "movie": "movie",
            "fav": "actor",
            "actor": "actor",
            "dir": "director",
            "director": "director",
            "movie_recom": "movie_recom",
        }
        searched_from = mapping.get(src, "movie")

    send_movie_card(
        call.message.chat.id,
        movie_id,
        effective_user_id,
        searched_from=searched_from,
        viewer_id=call.from_user.id,
    )
    bot.answer_callback_query(call.id)
