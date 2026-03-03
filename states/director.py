from telebot.handler_backends import State, StatesGroup


class DirectorSearchState(StatesGroup):
    waiting_for_director_name = State()
