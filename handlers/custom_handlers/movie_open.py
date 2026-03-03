from loader import bot
from utils.movie_service import send_movie_card


@bot.callback_query_handler(func=lambda c: c.data.startswith("movie_"))
def movie_callback(call):
    parts = call.data.split("_")
    # movie_{id} OR movie_{id}_{src}
    movie_id = int(parts[1])
    searched_from = "str"
    if len(parts) >= 3:
        src = parts[2]
        if src in ("fav", "dir"):
            searched_from = src

    send_movie_card(call.message.chat.id, movie_id, call.from_user.id, searched_from=searched_from)
