from telebot.types import Message
from keyboards.reply.main_menu import main_menu
from loader import bot


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    bot.reply_to(message, f"Hello, {message.from_user.full_name}!")
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=main_menu())
