from datetime import datetime

from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config_data.config import DATE_FORMAT
from loader import bot
from states.contacts import UserInfoState
from keyboards.reply.contact import request_contact
from database.models import User
from utils.i18n import LANG_EN, LANG_RU


_TEXT = {
    "en": {
        "choose_lang": "Choose language:",
        "already": "❗ You are already registered.",
        "enter_name": "Enter your name and surname (use space between them):",
        "enter_age": "Thanks. Now enter your age:",
        "enter_email": "Thanks. Now enter your contact email:",
        "send_contact": "Thanks. Send your contact information using the button below.",
        "name_invalid": "Name must contain only letters and space. Please enter again.",
        "age_invalid": "Age must contain only digits. Please enter again.",
        "email_invalid": "Email must be valid. Please enter again.",
        "contact_invalid": "Please send your contact information using the button below.",
        "done": "Registration complete:",
    },
    "ru": {
        "choose_lang": "Выберите язык:",
        "already": "❗ Вы уже зарегистрированы.",
        "enter_name": "Введите имя и фамилию (через пробел):",
        "enter_age": "Спасибо. Теперь введите ваш возраст:",
        "enter_email": "Спасибо. Теперь введите ваш email:",
        "send_contact": "Спасибо. Отправьте контакт через кнопку ниже.",
        "name_invalid": "Имя должно содержать только буквы и пробел. Введите ещё раз.",
        "age_invalid": "Возраст должен содержать только цифры. Введите ещё раз.",
        "email_invalid": "Email должен быть корректным. Введите ещё раз.",
        "contact_invalid": "Пожалуйста, отправьте контакт через кнопку ниже.",
        "done": "Регистрация завершена:",
    },
}


def _lang_markup() -> InlineKeyboardMarkup:
    m = InlineKeyboardMarkup()
    m.row(
        InlineKeyboardButton(text="English", callback_data="reg_lang:en"),
        InlineKeyboardButton(text="Русский", callback_data="reg_lang:ru"),
    )
    return m


def _is_registered(user: User) -> bool:
    return bool((user.email or "").strip()) and bool((user.phone_number or "").strip())


@bot.message_handler(commands=["registration"])
def registration(message: Message) -> None:
    existing = User.get_or_none(User.user_id == message.from_user.id)
    if existing and _is_registered(existing):
        bot.send_message(message.chat.id, _TEXT.get(getattr(existing, "language", "en"), _TEXT["en"])["already"])
        bot.delete_state(message.from_user.id, message.chat.id)
        return

    bot.set_state(message.from_user.id, UserInfoState.language, message.chat.id)
    bot.send_message(message.chat.id, f"{_TEXT['en']['choose_lang']} / {_TEXT['ru']['choose_lang']}", reply_markup=_lang_markup())


@bot.callback_query_handler(func=lambda c: c.data.startswith("reg_lang:"))
def set_reg_language(call: CallbackQuery):
    lang = call.data.split(":", 1)[1]
    if lang not in (LANG_EN, LANG_RU):
        bot.answer_callback_query(call.id, "Unknown language")
        return

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data["language"] = lang

    bot.set_state(call.from_user.id, UserInfoState.name, call.message.chat.id)
    bot.edit_message_text(_TEXT[lang]["enter_name"], call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.message_handler(state=UserInfoState.name)
def get_name(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data.get("language", "en")

    parts = (message.text or "").split()
    if len(parts) >= 1 and all(p.isalpha() for p in parts):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["name"] = parts[0]
            data["surname"] = parts[1] if len(parts) > 1 else ""

        bot.send_message(message.chat.id, _TEXT[lang]["enter_age"])
        bot.set_state(message.from_user.id, UserInfoState.age, message.chat.id)
    else:
        bot.send_message(message.chat.id, _TEXT[lang]["name_invalid"])


@bot.message_handler(state=UserInfoState.age)
def get_age(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data.get("language", "en")

    if (message.text or "").isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["age"] = int(message.text)

        bot.send_message(message.chat.id, _TEXT[lang]["enter_email"])
        bot.set_state(message.from_user.id, UserInfoState.email, message.chat.id)
    else:
        bot.send_message(message.chat.id, _TEXT[lang]["age_invalid"])


@bot.message_handler(state=UserInfoState.email)
def get_email(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data.get("language", "en")

    txt = (message.text or "").strip()
    if "@" in txt and "." in txt:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["email"] = txt

        bot.send_message(message.chat.id, _TEXT[lang]["send_contact"], reply_markup=request_contact())
        bot.set_state(message.from_user.id, UserInfoState.phone_number, message.chat.id)
    else:
        bot.send_message(message.chat.id, _TEXT[lang]["email_invalid"])


@bot.message_handler(content_types=["text", "contact"], state=UserInfoState.phone_number)
def get_contact(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data.get("language", "en")

    if message.content_type != "contact":
        bot.send_message(message.chat.id, _TEXT[lang]["contact_invalid"], reply_markup=request_contact())
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["phone_number"] = message.contact.phone_number
        data["reg_date"] = datetime.fromtimestamp(message.date).strftime(DATE_FORMAT)
        data["user_id"] = message.from_user.id
        data["username"] = message.from_user.username

        user = User.get_or_none(User.user_id == data["user_id"])
        if user is None:
            User.create(
                user_id=data["user_id"],
                username=data["username"],
                name=data.get("name", ""),
                surname=data.get("surname", ""),
                age=int(data.get("age") or 0),
                email=data.get("email", ""),
                phone_number=data.get("phone_number", ""),
                reg_date=data.get("reg_date"),
                language=data.get("language", "en"),
            )
        else:
            user.username = data["username"]
            user.name = data.get("name", "")
            user.surname = data.get("surname", "")
            user.age = int(data.get("age") or 0)
            user.email = data.get("email", "")
            user.phone_number = data.get("phone_number", "")
            user.reg_date = data.get("reg_date")
            user.language = data.get("language", getattr(user, "language", "en"))
            user.save()

        bot.send_message(
            message.chat.id,
            f"{_TEXT[lang]['done']}\n"
            f"Telegram ID: {data['user_id']}\n"
            f"Username: {data['username']}\n"
            f"Name: {data.get('name','')}\n"
            f"Surname: {data.get('surname','')}\n"
            f"Age: {data.get('age','')}\n"
            f"Email: {data.get('email','')}\n"
            f"Phone: {data.get('phone_number','')}\n"
            f"Registration Date: {data.get('reg_date','')}\n"
            f"Language: {data.get('language','')}"
        )

    bot.delete_state(message.from_user.id, message.chat.id)
