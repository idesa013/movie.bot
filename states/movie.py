from telebot.handler_backends import State, StatesGroup


class MovieSearchState(StatesGroup):
    waiting_for_title = State()
