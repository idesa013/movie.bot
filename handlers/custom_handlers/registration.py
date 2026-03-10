from datetime import datetime

from telebot.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)

from config_data.config import DATE_FORMAT
from loader import bot
from states.contacts import UserInfoState

from keyboards.reply.contact import request_contact
from keyboards.reply.admin_menu import get_main_menu

from database.models import User


def _reg_lang_markup() -> InlineKeyboardMarkup:
    m = InlineKeyboardMarkup()
    m.row(
        InlineKeyboardButton(text="English", callback_data="reg_lang:en"),
        InlineKeyboardButton(text="Русский", callback_data="reg_lang:ru"),
    )
    return m


def _is_fully_registered(user: User) -> bool:
    return bool((user.email or "").strip()) and bool((user.phone_number or "").strip())


@bot.message_handler(commands=["registration"])
def registration(message: Message) -> None:
    user_id = message.from_user.id
    chat_id = message.chat.id

    if User.select().where(User.user_id == user_id).exists():
        user = User.get(User.user_id == user_id)
        if _is_fully_registered(user):
            lang = getattr(user, "language", "en") or "en"
            bot.send_message(
                chat_id,
                "❗ You are already registered." if lang == "en" else "❗ Вы уже зарегистрированы.",
                reply_markup=get_main_menu(user_id, lang),
            )
            bot.delete_state(user_id, chat_id)
            return

    bot.set_state(user_id, UserInfoState.language, chat_id)
    bot.send_message(chat_id, "Choose language / Выберите язык:", reply_markup=_reg_lang_markup())


@bot.callback_query_handler(func=lambda c: c.data == "start_registration")
def start_registration_from_button(call: CallbackQuery):
    bot.set_state(call.from_user.id, UserInfoState.language, call.message.chat.id)
    bot.send_message(call.message.chat.id, "Choose language / Выберите язык:", reply_markup=_reg_lang_markup())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("reg_lang:"))
def registration_set_language(call: CallbackQuery):
    lang = call.data.split(":", 1)[1]
    if lang not in ("en", "ru"):
        bot.answer_callback_query(call.id, "Unknown language")
        return

    bot.set_state(call.from_user.id, UserInfoState.name, call.message.chat.id)

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data["language"] = lang

    bot.edit_message_text(
        "✅ Language selected. Now enter your name and surname (use space between them)" if lang == "en" else "✅ Язык выбран. Теперь введите имя и фамилию через пробел",
        call.message.chat.id,
        call.message.message_id,
    )
    bot.answer_callback_query(call.id)


@bot.message_handler(state=UserInfoState.name)
def get_name(message: Message) -> None:
    if all(part.isalpha() for part in message.text.split()):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["full_name"] = message.text
            lang = data.get("language", "en")

        bot.send_message(message.chat.id, "Thanks. Now enter your age" if lang == "en" else "Спасибо. Теперь введите ваш возраст")
        bot.set_state(message.from_user.id, UserInfoState.age, message.chat.id)
    else:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            lang = data.get("language", "en")

        bot.send_message(
            message.chat.id,
            "Name must contain only letters and space. Please enter your name again." if lang == "en" else "Имя должно содержать только буквы и пробел. Введите имя ещё раз.",
        )


@bot.message_handler(state=UserInfoState.age)
def get_age(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data.get("language", "en")

    if message.text.isdigit():
        bot.send_message(message.chat.id, "Thanks. Now enter your contact email" if lang == "en" else "Спасибо. Теперь введите email")
        bot.set_state(message.from_user.id, UserInfoState.email, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["age"] = message.text
    else:
        bot.send_message(
            message.chat.id,
            "Age must contain only digits. Please enter your age again." if lang == "en" else "Возраст должен содержать только цифры. Введите возраст ещё раз.",
        )


@bot.message_handler(state=UserInfoState.email)
def get_email(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data.get("language", "en")

    if "@" in message.text and "." in message.text:
        bot.send_message(
            message.chat.id,
            "Thanks. Send your contact information using the button below." if lang == "en" else "Спасибо. Отправьте контакт с помощью кнопки ниже.",
            reply_markup=request_contact(lang),
        )
        bot.set_state(message.from_user.id, UserInfoState.phone_number, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["email"] = message.text
    else:
        bot.send_message(
            message.chat.id,
            "Email must be a valid email address. Please enter your email again." if lang == "en" else "Email должен быть корректным. Введите email ещё раз.",
        )


@bot.message_handler(content_types=["text", "contact"], state=UserInfoState.phone_number)
def get_contact(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        lang = data.get("language", "en")

    if message.content_type != "contact":
        bot.send_message(
            message.chat.id,
            "Please send your contact information using the button below." if lang == "en" else "Пожалуйста, отправьте контакт с помощью кнопки ниже.",
            reply_markup=request_contact(lang),
        )
        return

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["phone_number"] = message.contact.phone_number
        data["reg_date"] = datetime.fromtimestamp(message.date).strftime(DATE_FORMAT)
        data["user_id"] = message.from_user.id
        data["username"] = message.from_user.username

        full_name = data.get("full_name", "").split()
        data["name"] = full_name[0] if len(full_name) >= 1 else ""
        data["surname"] = full_name[1] if len(full_name) >= 2 else ""

        language = data.get("language") or "en"

        if User.select().where(User.user_id == data["user_id"]).exists():
            user = User.get(User.user_id == data["user_id"])
            user.username = data["username"]
            user.name = data["name"]
            user.surname = data["surname"]
            user.age = int(data["age"])
            user.email = data["email"]
            user.phone_number = data["phone_number"]
            user.reg_date = data["reg_date"]
            user.language = language
            if getattr(user, "active", None) is None:
                user.active = True
            user.save()
        else:
            User.create(
                user_id=data["user_id"],
                username=data["username"],
                name=data["name"],
                surname=data["surname"],
                age=int(data["age"]),
                email=data["email"],
                phone_number=data["phone_number"],
                reg_date=data["reg_date"],
                language=language,
                active=True,
            )

        text = (
            f"Registration complete:\n"
            f"Telegram ID: {data['user_id']}\n"
            f"Telegram Username: {data['username']}\n"
            f"Name: {data['name']}\n"
            f"Surname: {data['surname']}\n"
            f"Age: {data['age']}\n"
            f"Email: {data['email']}\n"
            f"Phone: {data['phone_number']}\n"
            f"Registration Date: {data['reg_date']}\n"
            f"Language: {language}"
            if language == "en"
            else f"Регистрация завершена:\n"
            f"Telegram ID: {data['user_id']}\n"
            f"Username: {data['username']}\n"
            f"Имя: {data['name']}\n"
            f"Фамилия: {data['surname']}\n"
            f"Возраст: {data['age']}\n"
            f"Email: {data['email']}\n"
            f"Телефон: {data['phone_number']}\n"
            f"Дата регистрации: {data['reg_date']}\n"
            f"Язык: {language}"
        )

        bot.send_message(message.chat.id, text, reply_markup=ReplyKeyboardRemove())
        bot.send_message(message.chat.id, "Choose an action:" if language == "en" else "Выберите действие:", reply_markup=get_main_menu(message.from_user.id, language))

    bot.delete_state(message.from_user.id, message.chat.id)
