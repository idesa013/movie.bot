from datetime import datetime

from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from loader import bot
from config_data.config import DATE_FORMAT
from api.tmdb_movie import get_movie_details, get_movie_credits

from database.favorites import add_favorite, remove_favorite, check_favorite
from keyboards.inline.add_to_fav import add_favorites_button

from utils.i18n import get_user_language, tmdb_language, t


def _chunked(items, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _build_movie_markup(user_id: int, movie_id: int) -> InlineKeyboardMarkup:
    lang = get_user_language(user_id)
    tmdb_lang = tmdb_language(lang)

    credits = get_movie_credits(movie_id, language=tmdb_lang) or {}

    markup = InlineKeyboardMarkup()

    # 1) Directors — up to 3 per row
    directors = []
    seen_dir = set()
    for c in credits.get("crew", []) or []:
        if c.get("job") != "Director":
            continue
        dir_id = c.get("id")
        name = c.get("name")
        if dir_id is None or not name:
            continue
        if dir_id in seen_dir:
            continue
        seen_dir.add(dir_id)
        directors.append((dir_id, name))

    director_buttons = [
        InlineKeyboardButton(text=name, callback_data=f"director_{dir_id}")
        for dir_id, name in directors
    ]
    for row in _chunked(director_buttons, 3):
        markup.row(*row)

    # 2) Actors — up to 3 per row + primary
    actors = []
    seen_act = set()
    for a in (credits.get("cast", []) or [])[:15]:
        act_id = a.get("id")
        name = a.get("name")
        if act_id is None or not name:
            continue
        if act_id in seen_act:
            continue
        seen_act.add(act_id)
        actors.append((act_id, name))

    actor_buttons = [
        InlineKeyboardButton(
            text=name, callback_data=f"actor_{act_id}", style="primary"
        )
        for act_id, name in actors
    ]
    for row in _chunked(actor_buttons, 3):
        markup.row(*row)

    # 3) Favorites — last row (✅ IMPORTANT: pass lang)
    in_favorites = check_favorite(user_id, movie_id)
    fav_markup = add_favorites_button(movie_id, in_favorites=in_favorites, lang=lang)
    for row in fav_markup.keyboard:
        markup.row(*row)

    return markup


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(("add_fav:", "remove_fav:"))
)
def handle_favorites(call: CallbackQuery):
    user_id = call.from_user.id
    lang = get_user_language(user_id)

    movie_id = int(call.data.split(":")[1])

    # Movie title (try from caption/text)
    movie_name = "Movie"
    try:
        if getattr(call.message, "caption", None):
            first_line = call.message.caption.split("\n")[0]
        else:
            first_line = call.message.text.split("\n")[0]
        movie_name = (
            first_line.replace("🎬 ", "").replace("<b>", "").replace("</b>", "")
        )
        movie_name = movie_name.split(" (")[0].strip()
    except Exception:
        pass

    if call.data.startswith("add_fav:"):
        search_time = datetime.now().strftime(DATE_FORMAT)

        details = get_movie_details(movie_id) or {}
        genres = details.get("genres", []) or []
        genre_ids_str = (
            " ".join(str(g["id"]) for g in genres if g.get("id") is not None)
            if genres
            else ""
        )

        add_favorite(user_id, movie_id, search_time, genre_ids_str)

        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=_build_movie_markup(user_id, movie_id),
        )
        bot.answer_callback_query(call.id, t(lang, "fav_added").format(name=movie_name))
        return

    if call.data.startswith("remove_fav:"):
        remove_favorite(user_id, movie_id)

        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=_build_movie_markup(user_id, movie_id),
        )
        bot.answer_callback_query(
            call.id, t(lang, "fav_removed").format(name=movie_name)
        )
        return
