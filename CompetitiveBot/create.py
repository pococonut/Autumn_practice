from config import settings
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

bot = Bot(settings.api, parse_mode=ParseMode.HTML)
dp = Dispatcher()
