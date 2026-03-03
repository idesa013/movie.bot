from telebot.types import CallbackQuery
from loader import bot
from datetime import datetime
from config_data.config import DATE_FORMAT
from api.tmdb_director import get_director_details
from database.director_favorites import (
    add_director_favorite,
    remove_director_favorite,
    check_director_favorite,
)
from keyboards.inline.add_to_director_fav import add_director_favorites_button


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(("add_director_fav:", "remove_director_fav:"))
)
def handle_director_favorites(call: CallbackQuery):
    user_id = call.from_user.id
    director_id = int(call.data.split(":")[1])

    details = get_director_details(director_id) or {}
    director_name = details.get("name") or "Director"

    if call.data.startswith("add_director_fav:"):
        search_time = datetime.now().strftime(DATE_FORMAT)
        add_director_favorite(user_id, director_id, search_time)

        markup = add_director_favorites_button(director_id, in_favorites=True)
        bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id, reply_markup=markup
        )
        bot.answer_callback_query(call.id, f"{director_name} added to your Favorites")

    elif call.data.startswith("remove_director_fav:"):
        remove_director_favorite(user_id, director_id)

        markup = add_director_favorites_button(director_id, in_favorites=False)
        bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id, reply_markup=markup
        )
        bot.answer_callback_query(call.id, f"{director_name} removed from your Favorites")
