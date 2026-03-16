from telebot.types import Message

from loader import bot
from keyboards.reply.texts import MAIN_MENU_TEXT
from utils.i18n import get_user_language
from utils.access import ensure_user_not_blocked

from states.movie import MovieSearchState
from states.actor import ActorSearchState
from states.director import DirectorSearchState


def _has_state(message: Message) -> bool:
    state = bot.get_state(message.from_user.id, message.chat.id)
    return bool(state)


def _get_menu_texts(lang: str) -> dict:
    return MAIN_MENU_TEXT.get(lang, MAIN_MENU_TEXT["en"])


def _route_commands(message: Message) -> bool:
    txt = (message.text or "").strip()
    if not txt.startswith("/"):
        return False

    try:
        bot.delete_state(message.from_user.id, message.chat.id)
    except Exception:
        pass

    cmd = txt.split()[0].lower()

    if cmd == "/start":
        from handlers.default_handlers.start import bot_start

        bot_start(message)
        return True

    if cmd == "/help":
        from handlers.default_handlers.help import bot_help

        bot_help(message)
        return True

    if cmd == "/registration":
        from handlers.custom_handlers.registration import registration

        registration(message)
        return True

    return False


def _route_main_menu_buttons(message: Message) -> bool:
    lang = get_user_language(message.from_user.id)
    txt = (message.text or "").strip()
    menu = _get_menu_texts(lang)

    if txt == menu["movie"]:
        bot.set_state(
            message.from_user.id, MovieSearchState.waiting_for_title, message.chat.id
        )
        bot.send_message(
            message.chat.id,
            "Введите название фильма:" if lang == "ru" else "Enter movie title:",
        )
        return True

    if txt == menu["actor"]:
        bot.set_state(
            message.from_user.id,
            ActorSearchState.waiting_for_actor_name,
            message.chat.id,
        )
        bot.send_message(
            message.chat.id,
            "Введите имя актёра:" if lang == "ru" else "Enter actor name:",
        )
        return True

    if txt == menu["director"]:
        bot.set_state(
            message.from_user.id,
            DirectorSearchState.waiting_for_director_name,
            message.chat.id,
        )
        bot.send_message(
            message.chat.id,
            "Введите имя режиссёра:" if lang == "ru" else "Enter director name:",
        )
        return True

    return False


@bot.message_handler(func=lambda m: not _has_state(m), content_types=["text"])
def echo(message: Message):
    if _route_commands(message):
        return

    if not ensure_user_not_blocked(bot, message.chat.id, message.from_user.id):
        return

    if _route_main_menu_buttons(message):
        return

    lang = get_user_language(message.from_user.id)
    bot.send_message(
        message.chat.id,
        (
            "Эхо без состояния или фильтра.\nСообщение: "
            if lang == "ru"
            else "Echo (no state/filter).\nMessage: "
        )
        + (message.text or ""),
    )
