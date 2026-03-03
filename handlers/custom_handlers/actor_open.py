from loader import bot
from utils.person_service import send_actor_card


@bot.callback_query_handler(func=lambda c: c.data.startswith("actor_"))
def actor_callback(call):
    actor_id = int(call.data.split("_")[1])
    send_actor_card(call.message.chat.id, call.from_user.id, actor_id, searched_from="mov")
