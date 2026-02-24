from telebot.types import CallbackQuery
from loader import bot
from database.favorites import add_favorite, remove_favorite, check_favorite
from keyboards.inline.add_to_fav import add_favorites_button
from datetime import datetime
from config_data.config import DATE_FORMAT
from handlers.custom_handlers.movie_search import bot_data  # <-- импортируем словарь


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(("add_fav:", "remove_fav:"))
)
def handle_favorites(call: CallbackQuery):
    user_id = call.from_user.id
    movie_id = int(call.data.split(":")[1])
    data = bot_data.get(user_id, {})
    genre_ids = data.get("genre_ids", "")

    # Сохраним movie_name в словаре или в call.message.text
    # Здесь просто вытаскиваем из текста сообщения
    try:
        movie_name_line = call.message.text.split("\n")[
            0
        ]  # первая строка с названием фильма
        movie_name = movie_name_line.replace("🎬 ", "").split(" (")[0]
    except Exception:
        movie_name = "Movie"

    if call.data.startswith("add_fav:"):
        search_time = datetime.now().strftime(DATE_FORMAT)
        add_favorite(user_id, movie_id, search_time, genre_ids)
        markup = add_favorites_button(movie_id, in_favorites=True)
        bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id, reply_markup=markup
        )
        bot.answer_callback_query(call.id, f"{movie_name} added to your Favorites")

    elif call.data.startswith("remove_fav:"):
        remove_favorite(user_id, movie_id)
        markup = add_favorites_button(movie_id, in_favorites=False)
        bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id, reply_markup=markup
        )
        bot.answer_callback_query(call.id, f"{movie_name} removed from your Favorites")
