from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    user_id = State()
    username = State()
    name = State()
    surname = State()
    age = State()
    email = State()
    phone_number = State()
    reg_date = State()
