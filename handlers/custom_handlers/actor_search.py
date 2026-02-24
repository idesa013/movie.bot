from telebot.types import Message
from loader import bot
from states.actor import ActorSearchState
from api.tmbd_actor import (
    search_actor,
    get_actor_details,
    get_actor_movie_credits,
)
from html import escape


@bot.message_handler(state=ActorSearchState.waiting_for_actor_name)
def process_actor_search(message: Message):
    query = message.text

    data = search_actor(query)
    results = data.get("results")

    if not results:
        bot.send_message(message.chat.id, "Actor not found")
        return

    actor = results[0]
    actor_id = actor.get("id")

    details = get_actor_details(actor_id)
    credits = get_actor_movie_credits(actor_id)

    text = (
        f"🎭 <b>{escape(details.get('name', ''))}</b>\n"
        f"📅 Birthday: <b>{details.get('birthday', 'n/a')}</b>\n"
        f"🌍 Place of birth: <b>{escape(details.get('place_of_birth', 'n/a'))}</b>\n\n"
    )

    biography = details.get("biography") or "No biography available"
    text += f"{escape(biography[:1000])}\n\n"

    text += "🎬 Known for:\n"

    movies = credits.get("cast", [])[:8]
    for movie in movies:
        title = escape(movie.get("title", ""))
        character = escape(movie.get("character", ""))
        text += f"• {title} — {character}\n"

    if details.get("profile_path"):
        photo = "https://image.tmdb.org/t/p/w500" + details["profile_path"]
        bot.send_photo(message.chat.id, photo)

    bot.send_message(message.chat.id, text, parse_mode="HTML")

    bot.delete_state(message.from_user.id, message.chat.id)
