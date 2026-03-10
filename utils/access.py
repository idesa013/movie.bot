from database.models import User
from keyboards.inline.blocked_user import blocked_user_markup


def is_user_blocked(user_id: int) -> bool:
    user = User.get_or_none(User.user_id == user_id)

    if not user:
        return False

    return not bool(getattr(user, "active", True))


def ensure_user_not_blocked(bot, chat_id: int, user_id: int) -> bool:
    """
    Проверяет, заблокирован ли пользователь.
    Если да — показывает сообщение и кнопку написать администратору.
    """

    if not is_user_blocked(user_id):
        return True

    # ленивый импорт чтобы избежать circular import
    from utils.i18n import get_user_language

    lang = get_user_language(user_id)

    text = (
        "⛔ Вы заблокированы. Обратитесь к администратору."
        if lang == "ru"
        else "⛔ You are blocked. Contact the administrator."
    )

    bot.send_message(
        chat_id,
        text,
        reply_markup=blocked_user_markup(lang),
    )

    return False
