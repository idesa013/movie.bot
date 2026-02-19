from datetime import datetime
from config_data.config import DATE_FORMAT
from loader import bot
from states.contacts import UserInfoState
from telebot.types import Message
from keyboards.reply.contact import request_contact
from database.models import User


@bot.message_handler(commands=["registration"])
def registration(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.name, message.chat.id)

    # ✅ ПРОВЕРКА: есть ли пользователь
    if User.select().where(User.user_id == message.from_user.id).exists():
        bot.send_message(message.from_user.id, "❗ You are already registered.")
        bot.delete_state(message.from_user.id, message.chat.id)
        return

    bot.send_message(
        message.from_user.id,
        f"<b>{message.from_user.username}</b>, enter your name and surname (use space beetween them)",
        parse_mode="HTML",
    )


@bot.message_handler(state=UserInfoState.name)
def get_name(message: Message) -> None:
    if all(part.isalpha() for part in message.text.split()):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["full_name"] = message.text

        bot.send_message(message.from_user.id, "Thanks. Now enter your age")
        bot.set_state(message.from_user.id, UserInfoState.age, message.chat.id)
    else:
        bot.send_message(
            message.from_user.id,
            "Name must contain only letters and space. Please enter your name again.",
        )


@bot.message_handler(state=UserInfoState.age)
def get_age(message: Message) -> None:
    if message.text.isdigit():
        bot.send_message(message.from_user.id, "Thanks. Now enter your contact email")
        bot.set_state(message.from_user.id, UserInfoState.email, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["age"] = message.text
    else:
        bot.send_message(
            message.from_user.id,
            "Age must contain only digits. Please enter your age again.",
        )


@bot.message_handler(state=UserInfoState.email)
def get_email(message: Message) -> None:
    if "@" in message.text and "." in message.text:
        bot.send_message(
            message.from_user.id,
            "Thanks. Send your contact information using the button below.",
            reply_markup=request_contact(),
        )
        bot.set_state(message.from_user.id, UserInfoState.phone_number, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["email"] = message.text
    else:
        bot.send_message(
            message.from_user.id,
            "Email must be a valid email address. Please enter your email again.",
        )


@bot.message_handler(
    content_types=["text", "contact"], state=UserInfoState.phone_number
)
def get_contact(message: Message) -> None:
    if message.content_type == "contact":
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["phone_number"] = message.contact.phone_number
            data["reg_date"] = datetime.fromtimestamp(message.date).strftime(
                DATE_FORMAT
            )
            data["user_id"] = message.from_user.id
            data["username"] = message.from_user.username
            data["name"] = data.get("full_name", "").split()[0]
            data["surname"] = (
                data.get("full_name", "").split()[1]
                if len(data.get("full_name", "").split()) > 0
                else ""
            )

            # ✅ СОХРАНЕНИЕ В БД
            User.create(
                user_id=data["user_id"],
                username=data["username"],
                name=data["name"],
                surname=data["surname"],
                age=int(data["age"]),
                email=data["email"],
                phone_number=data["phone_number"],
                reg_date=data["reg_date"],
            )

            text = (
                f"Registration complete:\nTelegra ID: {data['user_id']}\nTelegram Username: {data['username']}\n"
                f"Name: {data['name']}\nSurname: {data['surname']}\nAge: {data['age']}\n"
                f"Email: {data['email']}\nPhone: {data['phone_number']}\nRegistration Date: {data['reg_date']}"
            )
            bot.send_message(message.from_user.id, text)
        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(
            message.from_user.id,
            "Please send your contact information using the button below.",
        )
