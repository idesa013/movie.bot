from loader import bot
from utils.person_service import send_director_card
from utils.i18n import ensure_registered
from utils.admin_context import resolve_effective_user_id


@bot.callback_query_handler(func=lambda c: c.data.startswith("director_recom:"))
def director_recom_callback(call):
    if not ensure_registered(bot, call.message.chat.id, call.from_user.id):
        bot.answer_callback_query(call.id)
        return

    director_id = int(call.data.split(":")[1])
    effective_user_id = resolve_effective_user_id(call.from_user.id)
    send_director_card(
        call.message.chat.id,
        effective_user_id,
        director_id,
        searched_from="director_recom",
        viewer_id=call.from_user.id,
    )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("director_"))
def director_callback(call):
    if not ensure_registered(bot, call.message.chat.id, call.from_user.id):
        bot.answer_callback_query(call.id)
        return

    director_id = int(call.data.split("_")[1])
    effective_user_id = resolve_effective_user_id(call.from_user.id)
    send_director_card(
        call.message.chat.id,
        effective_user_id,
        director_id,
        searched_from="movie",
        viewer_id=call.from_user.id,
    )
    bot.answer_callback_query(call.id)
