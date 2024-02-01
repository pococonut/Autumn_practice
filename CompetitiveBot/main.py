import asyncio
import logging
import sys
from aiogram.methods import DeleteWebhook
from commands.url_requests import read_teams
from create import dp, bot
from aiogram import types, F
from aiogram.filters.command import Command, CommandStart
from keyboards import menu_keyboard, registration_ikb
from commands import get_tasks, get_languages, submit_solution, get_result, get_scoreboard, add_user, get_user_info

logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

DESCRIPTION = ("Телеграм бот предоставляет список доступных задач по программированию трех уровней сложности. "
               "Решения принимаются на нескольких доступных языках, благодаря чему, вы можете проверить свои навыки в "
               "каждом из них.\n\nТакже бот выводит рейтинговую таблицу, где вы можете увидеть свое место среди других "
               "пользователей. Это поможет вам отслеживать свой прогресс и стремиться к новым результатам.")


@dp.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer("Добро пожаловать!\n\n" + DESCRIPTION, reply_markup=registration_ikb)


def get_menu(u_id):
    """
    Функция возвращает меню если пользователь зарегистрирован, иначе предлагает пройти этап регистрации
    Args:
        u_id: Уникальный идентификатор пользователя в телеграм
    Returns: Текст сообщения и меню
    """
    already_exist = [True for t in read_teams() if str(u_id) in t.get("name")]
    if already_exist:
        return ["Выберите команду.", menu_keyboard]
    return ["Пройдите этап регистрации.", registration_ikb]


@dp.message(Command('menu'))
async def menu_command(message: types.Message):
    data = get_menu(message.from_user.id)
    await message.answer(data[0], reply_markup=data[1])


@dp.callback_query(F.data == 'menu_inline')
async def menu_command_inline(callback: types.CallbackQuery):
    data = get_menu(callback.from_user.id)
    await callback.message.edit_text(data[0], reply_markup=data[1])


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

