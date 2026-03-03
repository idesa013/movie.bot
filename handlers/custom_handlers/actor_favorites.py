from telebot.types import CallbackQuery
from loader import bot
from datetime import datetime
from config_data.config import DATE_FORMAT
from api.tmdb_actor import get_actor_details
from database.actor_favorites import (
    add_actor_favorite,
    remove_actor_favorite,
    check_actor_favorite,
)
from keyboards.inline.add_to_actor_fav import add_actor_favorites_button


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(("add_actor_fav:", "remove_actor_fav:"))
)
def handle_actor_favorites(call: CallbackQuery):
    user_id = call.from_user.id
    actor_id = int(call.data.split(":")[1])

    details = get_actor_details(actor_id) or {}
    actor_name = details.get("name") or "Actor"

    if call.data.startswith("add_actor_fav:"):
        search_time = datetime.now().strftime(DATE_FORMAT)
        add_actor_favorite(user_id, actor_id, search_time)

        markup = add_actor_favorites_button(actor_id, in_favorites=True)
        bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id, reply_markup=markup
        )
        bot.answer_callback_query(call.id, f"{actor_name} added to your Favorites")

    elif call.data.startswith("remove_actor_fav:"):
        remove_actor_favorite(user_id, actor_id)

        markup = add_actor_favorites_button(actor_id, in_favorites=False)
        bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id, reply_markup=markup
        )
        bot.answer_callback_query(call.id, f"{actor_name} removed from your Favorites")
