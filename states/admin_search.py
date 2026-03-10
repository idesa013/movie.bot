from telebot.handler_backends import StatesGroup, State


class AdminSearchState(StatesGroup):
    waiting_username = State()
    waiting_blocked_username = State()
