from telebot import types
from loader import bot
from api.tmdb_movie import get_movie_details, get_movie_credits  # твои функции для TMDB
from html import escape
from database.favorites import check_favorite
from keyboards.inline.add_to_fav import add_favorites_button


def send_movie_card(chat_id: int, movie_id: int, user_id: int):
    # Подробная информация о фильме
    details = get_movie_details(movie_id)
    credits = get_movie_credits(movie_id)

    # Жанры
    genres = details.get("genres", [])
    genres_text = ", ".join(f"<b>{g['name']}</b>" for g in genres) or "n/a"
    genre_ids_str = " ".join(str(g["id"]) for g in genres) if genres else ""

    # Режиссёры
    directors_list = [
        f'<a href="https://www.google.com/search?q={escape(d)}+director">{escape(d)}</a>'
        for d in [
            c["name"] for c in credits.get("crew", []) if c.get("job") == "Director"
        ]
    ]
    directors_text = ", ".join(directors_list) if directors_list else "n/a"

    # Текст карточки
    text = (
        f"🎬 {escape(details.get('title', ''))} (<b>{escape(details.get('original_title', ''))}</b>)\n"
        f"📅 Release Date: <b>{details.get('release_date', 'n/a')}</b>\n"
        f"⭐ Rating: <b>{details.get('vote_average', 'n/a')}</b>\n"
        f"🎭 Жанры: {genres_text}\n"
        f"🎬 Режиссёры: {directors_text}\n\n"
        f"{escape(details.get('overview', 'No description available'))}\n\n"
        f"👥 Starring:\n"
    )

    # Актёры
    for actor in credits.get("cast", [])[:8]:
        name = escape(actor["name"])
        char = escape(actor["character"])
        google = f"https://www.google.com/search?q={name}+actor"
        text += f'<a href="{google}">{name}</a> — {char}\n'

    # Постер
    if details.get("poster_path"):
        poster = "https://image.tmdb.org/t/p/w500" + details["poster_path"]
        bot.send_photo(chat_id, poster)

    # Проверка избранного
    in_favorites = check_favorite(user_id, movie_id)
    markup = add_favorites_button(movie_id, in_favorites=in_favorites)

    # Отправка текста
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
