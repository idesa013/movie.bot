import math
from telebot.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from loader import bot
from database.models import User
from database.block_log import add_block_log, get_last_block_time
from database.user_messages import get_user_messages_from_date, get_all_user_messages
from database.bot_config import get_config_int
from keyboards.reply.admin_menu import _TEXT, is_admin, get_main_menu, admin_panel_menu
from utils.i18n import get_user_language
from utils.admin_context import set_selected_user
from handlers.custom_handlers.favorites_view import send_favorites_list
from states.admin_search import AdminSearchState


ADMIN_PAGES = {}
ADMIN_MODE = {}  # users / messages


def _users_per_page() -> int:
    return get_config_int("user_per_admin_page", 3)


def _deny_if_not_admin(obj) -> bool:
    if is_admin(obj.from_user.id):
        return False

    lang = get_user_language(obj.from_user.id)
    chat_id = obj.message.chat.id if hasattr(obj, "message") else obj.chat.id
    bot.send_message(
        chat_id, "⛔ Access denied." if lang == "en" else "⛔ Доступ запрещён."
    )
    return True


def _safe_username(username):
    return f"@{username}" if username else "—"


def _users_pagination_markup(page, total_pages):
    markup = InlineKeyboardMarkup()
    row = []

    if page > 1:
        row.append(
            InlineKeyboardButton("⬅", callback_data=f"admin_users_page:{page-1}")
        )
    if page < total_pages:
        row.append(
            InlineKeyboardButton("➡", callback_data=f"admin_users_page:{page+1}")
        )

    if row:
        markup.row(*row)

    return markup


def _get_users_page(page: int):
    per_page = _users_per_page()
    query = User.select().order_by(User.id.asc())
    total = query.count()

    if total == 0:
        return [], 0, 0

    total_pages = math.ceil(total / per_page)
    page = max(1, min(page, total_pages))
    users = list(query.paginate(page, per_page))
    return users, total, total_pages


def _get_blocked_users_page(page: int):
    per_page = _users_per_page()
    query = User.select().where(User.active == False).order_by(User.id.asc())
    total = query.count()

    if total == 0:
        return [], 0, 0

    total_pages = math.ceil(total / per_page)
    page = max(1, min(page, total_pages))
    users = list(query.paginate(page, per_page))
    return users, total, total_pages


def _users_text(users, page, total_pages, lang):
    lines = [
        (
            f"👥 Users | Page {page}/{total_pages}"
            if lang == "en"
            else f"👥 Пользователи | Страница {page}/{total_pages}"
        ),
        "",
        (
            "Send user table ID to open the card."
            if lang == "en"
            else "Отправьте ID пользователя из таблицы, чтобы открыть карточку."
        ),
        "",
    ]

    for user in users:
        status_icon = "✅" if user.active else "⛔"
        lines.append(f"{user.id}. {_safe_username(user.username)} {status_icon}")

    return "\n".join(lines)


def _blocked_users_text(users, page, total_pages, lang):
    lines = [
        (
            f"✉ Blocked Users | Page {page}/{total_pages}"
            if lang == "en"
            else f"✉ Заблокированные | Страница {page}/{total_pages}"
        ),
        "",
        (
            "Send user table ID to open messages."
            if lang == "en"
            else "Отправьте ID пользователя из таблицы, чтобы открыть сообщения."
        ),
        "",
    ]

    for user in users:
        lines.append(f"{user.id}. {_safe_username(user.username)} ⛔")

    return "\n".join(lines)


def _show_users_page(chat_id, admin_id, page, edit_message=None):
    lang = get_user_language(admin_id)
    users, total, total_pages = _get_users_page(page)

    if total == 0:
        bot.send_message(
            chat_id, "No users found." if lang == "en" else "Пользователи не найдены."
        )
        return

    ADMIN_PAGES[admin_id] = page
    ADMIN_MODE[admin_id] = "users"

    text = _users_text(users, page, total_pages, lang)
    markup = _users_pagination_markup(page, total_pages)

    if edit_message:
        try:
            bot.edit_message_text(
                text, chat_id, edit_message.message_id, reply_markup=markup
            )
            return
        except Exception:
            pass

    bot.send_message(chat_id, text, reply_markup=markup)


def _show_blocked_users_page(chat_id, admin_id, page, edit_message=None):
    lang = get_user_language(admin_id)
    users, total, total_pages = _get_blocked_users_page(page)

    if total == 0:
        bot.send_message(
            chat_id,
            (
                "No blocked users."
                if lang == "en"
                else "Нет заблокированных пользователей."
            ),
        )
        return

    ADMIN_PAGES[admin_id] = page
    ADMIN_MODE[admin_id] = "messages"

    text = _blocked_users_text(users, page, total_pages, lang)
    markup = _users_pagination_markup(page, total_pages)

    if edit_message:
        try:
            bot.edit_message_text(
                text, chat_id, edit_message.message_id, reply_markup=markup
            )
            return
        except Exception:
            pass

    bot.send_message(chat_id, text, reply_markup=markup)


def _user_card_text(user, lang):
    full_name = f"{user.name or ''} {user.surname or ''}".strip() or "—"

    if lang == "en":
        return (
            "👤 User Card\n\n"
            f"Table ID: {user.id}\n"
            f"Telegram ID: {user.user_id}\n"
            f"Username: {_safe_username(user.username)}\n"
            f"Name: {full_name}\n"
            f"Age: {user.age}\n"
            f"Email: {user.email or '—'}\n"
            f"Phone: {user.phone_number or '—'}\n"
            f"Language: {user.language or '—'}\n"
            f"Status: {'Active' if user.active else 'Blocked'}\n"
            f"Registered: {user.reg_date}"
        )

    return (
        "👤 Карточка пользователя\n\n"
        f"ID в таблице: {user.id}\n"
        f"Telegram ID: {user.user_id}\n"
        f"Username: {_safe_username(user.username)}\n"
        f"Имя: {full_name}\n"
        f"Возраст: {user.age}\n"
        f"Email: {user.email or '—'}\n"
        f"Телефон: {user.phone_number or '—'}\n"
        f"Язык: {user.language or '—'}\n"
        f"Статус: {'Активен' if user.active else 'Заблокирован'}\n"
        f"Дата регистрации: {user.reg_date}"
    )


def _user_card_markup(user, page, lang):
    markup = InlineKeyboardMarkup()

    movies = "🎬 Movies" if lang == "en" else "🎬 Фильмы"
    actors = "🎭 Actors" if lang == "en" else "🎭 Актеры"
    directors = "🎬 Directors" if lang == "en" else "🎬 Режиссеры"
    back_btn = "⬅ Back to List" if lang == "en" else "⬅ Назад к списку"

    markup.row(
        InlineKeyboardButton(
            movies, callback_data=f"admin_user_fav:movies:{user.user_id}:{page}"
        ),
        InlineKeyboardButton(
            actors, callback_data=f"admin_user_fav:actors:{user.user_id}:{page}"
        ),
        InlineKeyboardButton(
            directors, callback_data=f"admin_user_fav:directors:{user.user_id}:{page}"
        ),
    )

    if not is_admin(user.user_id):
        block_btn = (
            ("⛔ Block" if user.active else "✅ Unblock")
            if lang == "en"
            else ("⛔ Заблокировать" if user.active else "✅ Разблокировать")
        )
        markup.row(
            InlineKeyboardButton(
                block_btn, callback_data=f"admin_user_toggle_block:{user.id}:{page}"
            )
        )

    markup.row(
        InlineKeyboardButton(back_btn, callback_data=f"admin_user_back_to_list:{page}")
    )
    return markup


def _send_user_card(chat_id, admin_id, table_id, page, edit_message=None):
    lang = get_user_language(admin_id)
    user = User.get_or_none(User.id == table_id)

    if not user:
        bot.send_message(
            chat_id, "User not found." if lang == "en" else "Пользователь не найден."
        )
        return

    set_selected_user(admin_id, user.user_id, page)
    text = _user_card_text(user, lang)
    markup = _user_card_markup(user, page, lang)

    if edit_message:
        try:
            bot.edit_message_text(
                text, chat_id, edit_message.message_id, reply_markup=markup
            )
            return
        except Exception:
            pass

    bot.send_message(chat_id, text, reply_markup=markup)


def _format_user_messages(user, lang: str):
    last_block_time = get_last_block_time(user.user_id)
    messages = get_user_messages_from_date(user.user_id, last_block_time)

    fallback_used = False
    if not messages:
        messages = get_all_user_messages(user.user_id)
        fallback_used = True

    if lang == "en":
        title = f"✉ Messages from {_safe_username(user.username)}"
        if last_block_time:
            title += f"\nSince last block: {last_block_time}"
        if fallback_used and messages:
            title += "\n(showing all messages because nothing was found after the last block)"
    else:
        title = f"✉ Сообщения от {_safe_username(user.username)}"
        if last_block_time:
            title += f"\nС последней блокировки: {last_block_time}"
        if fallback_used and messages:
            title += "\n(показаны все сообщения, так как после последней блокировки ничего не найдено)"

    if not messages:
        empty = "No messages." if lang == "en" else "Сообщений нет."
        return f"{title}\n\n{empty}"

    lines = [title, ""]
    for _msg_id, _user_id, _username, user_msg, created_at in messages:
        lines.append(f"[{created_at}]")
        lines.append(user_msg)
        lines.append("")

    return "\n".join(lines)


def _blocked_user_messages_markup(page: int, lang: str):
    markup = InlineKeyboardMarkup()
    back_text = "⬅ Back to List" if lang == "en" else "⬅ Назад к списку"
    markup.row(
        InlineKeyboardButton(
            back_text, callback_data=f"admin_messages_back_to_list:{page}"
        )
    )
    return markup


@bot.message_handler(
    func=lambda m: (m.text or "").strip()
    in (_TEXT["en"]["admin_panel"], _TEXT["ru"]["admin_panel"])
)
def open_admin_panel(message: Message):
    if _deny_if_not_admin(message):
        return

    try:
        bot.delete_state(message.from_user.id, message.chat.id)
    except Exception:
        pass

    set_selected_user(message.from_user.id, None)
    ADMIN_MODE[message.from_user.id] = "users"
    ADMIN_PAGES[message.from_user.id] = 1

    lang = get_user_language(message.from_user.id)
    bot.send_message(
        message.chat.id,
        "Choose an action:" if lang == "en" else "Выберите действие:",
        reply_markup=admin_panel_menu(lang),
    )


@bot.message_handler(
    func=lambda m: (m.text or "").strip()
    in (_TEXT["en"]["users"], _TEXT["ru"]["users"])
)
def show_users_list(message: Message):
    if _deny_if_not_admin(message):
        return

    try:
        bot.delete_state(message.from_user.id, message.chat.id)
    except Exception:
        pass

    set_selected_user(message.from_user.id, None)
    _show_users_page(message.chat.id, message.from_user.id, 1)


@bot.message_handler(
    func=lambda m: (m.text or "").strip()
    in (_TEXT["en"]["messages"], _TEXT["ru"]["messages"])
)
def open_blocked_messages_users(message: Message):
    if _deny_if_not_admin(message):
        return

    try:
        bot.delete_state(message.from_user.id, message.chat.id)
    except Exception:
        pass

    set_selected_user(message.from_user.id, None)
    _show_blocked_users_page(message.chat.id, message.from_user.id, 1)


@bot.message_handler(
    func=lambda m: (m.text or "").strip()
    in (_TEXT["en"]["search_user"], _TEXT["ru"]["search_user"])
)
def admin_search_user(message: Message):
    if _deny_if_not_admin(message):
        return

    lang = get_user_language(message.from_user.id)
    bot.set_state(
        message.from_user.id, AdminSearchState.waiting_username, message.chat.id
    )
    bot.send_message(
        message.chat.id,
        "Введите username пользователя" if lang == "ru" else "Enter username",
    )


@bot.message_handler(
    func=lambda m: (m.text or "").strip()
    in (_TEXT["en"]["search_blocked"], _TEXT["ru"]["search_blocked"])
)
def admin_search_blocked_user(message: Message):
    if _deny_if_not_admin(message):
        return

    lang = get_user_language(message.from_user.id)
    bot.set_state(
        message.from_user.id, AdminSearchState.waiting_blocked_username, message.chat.id
    )
    bot.send_message(
        message.chat.id,
        (
            "Введите username заблокированного пользователя"
            if lang == "ru"
            else "Enter blocked username"
        ),
    )


@bot.message_handler(state=AdminSearchState.waiting_username)
def admin_find_user(message: Message):
    if _deny_if_not_admin(message):
        return

    lang = get_user_language(message.from_user.id)
    username = (message.text or "").strip().replace("@", "")

    if not username:
        bot.send_message(
            message.chat.id,
            (
                "Введите username ещё раз или нажмите 'Назад в меню'."
                if lang == "ru"
                else "Enter username again or press 'Back to Menu'."
            ),
        )
        return

    user = User.get_or_none(User.username == username)

    if not user:
        bot.send_message(
            message.chat.id,
            (
                "Пользователь не найден. Попробуйте ещё раз или нажмите 'Назад в меню'."
                if lang == "ru"
                else "User not found. Try again or press 'Back to Menu'."
            ),
        )
        return

    bot.delete_state(message.from_user.id, message.chat.id)
    _send_user_card(message.chat.id, message.from_user.id, user.id, 1)


@bot.message_handler(state=AdminSearchState.waiting_blocked_username)
def admin_find_blocked_user(message: Message):
    if _deny_if_not_admin(message):
        return

    lang = get_user_language(message.from_user.id)
    username = (message.text or "").strip().replace("@", "")

    if not username:
        bot.send_message(
            message.chat.id,
            (
                "Введите username ещё раз или нажмите 'Назад в меню'."
                if lang == "ru"
                else "Enter username again or press 'Back to Menu'."
            ),
        )
        return

    user = User.get_or_none((User.username == username) & (User.active == False))

    if not user:
        bot.send_message(
            message.chat.id,
            (
                "Заблокированный пользователь не найден. Попробуйте ещё раз или нажмите 'Назад в меню'."
                if lang == "ru"
                else "Blocked user not found. Try again or press 'Back to Menu'."
            ),
        )
        return

    bot.delete_state(message.from_user.id, message.chat.id)
    _send_user_card(message.chat.id, message.from_user.id, user.id, 1)


@bot.callback_query_handler(func=lambda c: c.data.startswith("admin_users_page:"))
def admin_users_page_callback(call: CallbackQuery):
    if _deny_if_not_admin(call):
        return

    page = int(call.data.split(":")[1])
    mode = ADMIN_MODE.get(call.from_user.id, "users")

    if mode == "messages":
        _show_blocked_users_page(
            call.message.chat.id, call.from_user.id, page, edit_message=call.message
        )
    else:
        _show_users_page(
            call.message.chat.id, call.from_user.id, page, edit_message=call.message
        )

    bot.answer_callback_query(call.id)


@bot.message_handler(
    func=lambda m: is_admin(m.from_user.id) and (m.text or "").strip().isdigit()
)
def open_user_by_table_id(message: Message):
    table_id = int((message.text or "").strip())
    lang = get_user_language(message.from_user.id)
    user = User.get_or_none(User.id == table_id)

    if not user:
        bot.send_message(
            message.chat.id,
            (
                "User with this table ID not found."
                if lang == "en"
                else "Пользователь с таким ID в таблице не найден."
            ),
        )
        return

    mode = ADMIN_MODE.get(message.from_user.id, "users")
    page = ADMIN_PAGES.get(message.from_user.id, 1)

    if mode == "messages":
        if user.active:
            bot.send_message(
                message.chat.id,
                (
                    "This user is not blocked."
                    if lang == "en"
                    else "Этот пользователь не заблокирован."
                ),
            )
            return

        text = _format_user_messages(user, lang)
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=_blocked_user_messages_markup(page, lang),
        )
        return

    _send_user_card(message.chat.id, message.from_user.id, table_id, page)


@bot.callback_query_handler(
    func=lambda c: c.data.startswith("admin_user_back_to_list:")
)
def admin_back_to_list(call: CallbackQuery):
    if _deny_if_not_admin(call):
        return

    page = int(call.data.split(":")[1])
    set_selected_user(call.from_user.id, None)
    _show_users_page(
        call.message.chat.id, call.from_user.id, page, edit_message=call.message
    )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(
    func=lambda c: c.data.startswith("admin_messages_back_to_list:")
)
def admin_messages_back_to_list(call: CallbackQuery):
    if _deny_if_not_admin(call):
        return

    page = int(call.data.split(":")[1])
    set_selected_user(call.from_user.id, None)
    _show_blocked_users_page(
        call.message.chat.id, call.from_user.id, page, edit_message=call.message
    )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(
    func=lambda c: c.data.startswith("admin_user_back_to_card:")
)
def admin_back_to_card(call: CallbackQuery):
    if _deny_if_not_admin(call):
        return

    _, user_id, page = call.data.split(":")
    user = User.get_or_none(User.user_id == int(user_id))

    if user:
        _send_user_card(
            call.message.chat.id,
            call.from_user.id,
            user.id,
            int(page),
            edit_message=call.message,
        )

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(
    func=lambda c: c.data.startswith("admin_user_toggle_block:")
)
def admin_toggle_block(call: CallbackQuery):
    if _deny_if_not_admin(call):
        return

    _, table_id, page = call.data.split(":")
    user = User.get_or_none(User.id == int(table_id))
    lang = get_user_language(call.from_user.id)

    if not user:
        bot.answer_callback_query(
            call.id, "User not found" if lang == "en" else "Пользователь не найден"
        )
        return

    if is_admin(user.user_id):
        bot.answer_callback_query(
            call.id,
            (
                "Admin cannot be blocked"
                if lang == "en"
                else "Администратора нельзя заблокировать"
            ),
        )
        return

    user.active = not bool(user.active)
    user.save()

    add_block_log(
        user_id=user.user_id,
        admin_id=call.from_user.id,
        action="unblock" if user.active else "block",
    )

    _send_user_card(
        call.message.chat.id,
        call.from_user.id,
        user.id,
        int(page),
        edit_message=call.message,
    )
    bot.answer_callback_query(
        call.id, "Status updated" if lang == "en" else "Статус обновлён"
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("admin_user_fav:"))
def admin_user_favorites(call: CallbackQuery):
    if _deny_if_not_admin(call):
        return

    _, fav_type, selected_user_id, page = call.data.split(":")
    selected_user_id = int(selected_user_id)
    page = int(page)

    set_selected_user(call.from_user.id, selected_user_id, page)
    send_favorites_list(
        chat_id=call.message.chat.id,
        viewer_id=call.from_user.id,
        target_user_id=selected_user_id,
        fav_type=fav_type,
        edit_message=call.message,
    )
    bot.answer_callback_query(call.id)


@bot.message_handler(
    func=lambda m: (m.text or "").strip()
    in (_TEXT["en"]["back_to_menu"], _TEXT["ru"]["back_to_menu"])
)
def admin_back_to_main_menu(message: Message):
    if _deny_if_not_admin(message):
        return

    try:
        bot.delete_state(message.from_user.id, message.chat.id)
    except Exception:
        pass

    set_selected_user(message.from_user.id, None)
    lang = get_user_language(message.from_user.id)
    bot.send_message(
        message.chat.id,
        "Выберите действие:" if lang == "ru" else "Choose an action:",
        reply_markup=get_main_menu(message.from_user.id, lang),
    )
