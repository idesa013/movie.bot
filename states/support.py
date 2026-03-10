from telebot.handler_backends import StatesGroup, State


class SupportState(StatesGroup):
    waiting_for_message = State()
