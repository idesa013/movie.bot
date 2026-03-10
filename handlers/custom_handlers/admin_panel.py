from telebot.types import Message

from loader import bot
from database.models import User
from utils.i18n import get_user_language
from keyboards.reply.admin_menu import (
    _TEXT,
    is_admin,
    get_main_menu,
    admin_panel_menu,
)


def _deny_if_not_admin(message: Message) -> bool:
    if not is_admin(message.from_user.id):
        lang = get_user_language(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "⛔ Access denied." if lang == "en" else "⛔ Доступ запрещён.",
        )
        return True
    return False


@bot.message_handler(
    func=lambda m: (m.text or "").strip()
    in (_TEXT["en"]["admin_panel"], _TEXT["ru"]["admin_panel"])
)
def open_admin_panel(message: Message):
    if _deny_if_not_admin(message):
        return

    lang = get_user_language(message.from_user.id)
    bot.send_message(
        message.chat.id,
        _TEXT[lang]["admin_choose"],
        reply_markup=admin_panel_menu(lang),
    )


@bot.message_handler(
    func=lambda m: (m.text or "").strip()
    in (_TEXT["en"]["users"], _TEXT["ru"]["users"])
)
def show_users_list(message: Message):
    if _deny_if_not_admin(message):
        return

    lang = get_user_language(message.from_user.id)

    users = (
        User
        .select()
        .order_by(User.reg_date.desc())
    )

    total = users.count()

    if total == 0:
        bot.send_message(
            message.chat.id,
            "No users found." if lang == "en" else "Пользователи не найдены.",
            reply_markup=admin_panel_menu(lang),
        )
        return

    lines = [
        f"👥 Total users: {total}" if lang == "en" else f"👥 Всего пользователей: {total}",
        "",
        "Last 20 users:" if lang == "en" else "Последние 20 пользователей:",
        "",
    ]

    for idx, user in enumerate(users.limit(20), start=1):
        username = f"@{user.username}" if user.username else "—"
        full_name = f"{user.name or ''} {user.surname or ''}".strip() or "—"
        phone = user.phone_number or "—"
        email = user.email or "—"
        reg_date = str(user.reg_date)

        if lang == "en":
            lines.append(
                f"{idx}. ID: {user.user_id}\n"
                f"Username: {username}\n"
                f"Name: {full_name}\n"
                f"Phone: {phone}\n"
                f"Email: {email}\n"
                f"Language: {user.language}\n"
                f"Registered: {reg_date}"
            )
        else:
            lines.append(
                f"{idx}. ID: {user.user_id}\n"
                f"Username: {username}\n"
                f"Имя: {full_name}\n"
                f"Телефон: {phone}\n"
                f"Email: {email}\n"
                f"Язык: {user.language}\n"
                f"Зарегистрирован: {reg_date}"
            )

        lines.append("")

    text = "\n".join(lines)

    # Telegram ограничивает длину сообщения
    if len(text) <= 4000:
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=admin_panel_menu(lang),
        )
        return

    # если пользователей много и текст длинный — режем на части
    chunk = ""
    for line in lines:
        if len(chunk) + len(line) + 1 > 3500:
            bot.send_message(message.chat.id, chunk)
            chunk = line + "\n"
        else:
            chunk += line + "\n"

    if chunk.strip():
        bot.send_message(
            message.chat.id,
            chunk,
            reply_markup=admin_panel_menu(lang),
        )


@bot.message_handler(
    func=lambda m: (m.text or "").strip() == _TEXT["en"]["back"]
    or (m.text or "").strip() == _TEXT["ru"]["back"]
)
def admin_back_to_main(message: Message):
    if not is_admin(message.from_user.id):
        return

    lang = get_user_language(message.from_user.id)
    bot.send_message(
        message.chat.id,
        "Choose an action:" if lang == "en" else "Выберите действие:",
        reply_markup=get_main_menu(message.from_user.id, lang),
    )