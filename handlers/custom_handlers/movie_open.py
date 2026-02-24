from loader import bot
from utils.movie_service import send_movie_card


@bot.callback_query_handler(func=lambda c: c.data.startswith("movie_"))
def movie_callback(call):
    movie_id = int(call.data.split("_")[1])
    send_movie_card(call.message.chat.id, movie_id, call.from_user.id)
