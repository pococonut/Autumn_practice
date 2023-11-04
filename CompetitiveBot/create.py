from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import settings


bot = Bot(settings.api)
print(bot)
dp = Dispatcher(bot, storage=MemoryStorage())