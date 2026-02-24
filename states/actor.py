from telebot.handler_backends import State, StatesGroup


class ActorSearchState(StatesGroup):
    waiting_for_actor_name = State()
