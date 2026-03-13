from telebot import TeleBot
from telebot.storage import StateMemoryStorage
import telebot.apihelper
from config_data import config

storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)

telebot.apihelper.CONNECT_TIMEOUT = 15
telebot.apihelper.READ_TIMEOUT = 30
