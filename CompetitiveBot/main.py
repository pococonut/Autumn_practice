from aiogram.utils import executor
from create import dp
from aiogram import types
#from db.models.user import Base, engine
#from commands import
from keyboards import menu

commands = [
    types.BotCommand(command='/menu', description='Меню'),
    types.BotCommand(command='/change', description='Изменение данных'),
    types.BotCommand(command='/show', description='Просмотр данных'),
]


async def set_commands(dp):
    await dp.bot.set_my_commands(commands=commands, scope=types.BotCommandScopeAllPrivateChats())


DESCRIPTION = ""


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Добро пожаловать!\n\n" + DESCRIPTION)

@dp.message_handler(commands=['menu'])
async def menu_command(message: types.Message):
    await message.answer("Выберите команду\n\n", reply_markup=menu)

@dp.callback_handler(text='tasks')
async def tasks_command(message: types.Message):
    await message.answer("Выберите команду\n\n", reply_markup=menu)

#Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=set_commands, skip_updates=True)