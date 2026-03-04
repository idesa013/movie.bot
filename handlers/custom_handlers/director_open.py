from loader import bot
from utils.person_service import send_director_card


@bot.callback_query_handler(func=lambda c: c.data.startswith("director_"))
def director_callback(call):
    director_id = int(call.data.split("_")[1])
    send_director_card(call.message.chat.id, call.from_user.id, director_id, searched_from="movie")
