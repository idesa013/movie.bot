from loader import bot
from utils.person_service import send_actor_card
from utils.i18n import ensure_registered


@bot.callback_query_handler(func=lambda c: c.data.startswith("actor_recom:"))
def actor_recom_callback(call):
    if not ensure_registered(bot, call.message.chat.id, call.from_user.id):
        bot.answer_callback_query(call.id)
        return

    actor_id = int(call.data.split(":")[1])
    send_actor_card(
        call.message.chat.id,
        call.from_user.id,
        actor_id,
        searched_from="actor_recom",
    )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("actor_"))
def actor_callback(call):
    if not ensure_registered(bot, call.message.chat.id, call.from_user.id):
        bot.answer_callback_query(call.id)
        return

    actor_id = int(call.data.split("_")[1])
    send_actor_card(call.message.chat.id, call.from_user.id, actor_id, searched_from="movie")
    bot.answer_callback_query(call.id)