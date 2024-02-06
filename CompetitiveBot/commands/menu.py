from commands.general_func import read_user_values, write_user_values
from commands.url_requests import read_teams
from create import dp, bot
from aiogram import types, F
from aiogram.filters.command import Command, CommandStart
from keyboards import menu_keyboard, registration_ikb

global_Dict_del_msg = read_user_values("global_Dict_del_msg")

DESCRIPTION = ("Телеграм бот предоставляет список доступных задач по программированию трех уровней сложности. "
               "Решения принимаются на нескольких доступных языках, благодаря чему, вы можете проверить свои навыки в "
               "каждом из них.\n\nТакже бот выводит рейтинговую таблицу, где вы можете увидеть свое место среди других "
               "пользователей. Это поможет вам отслеживать свой прогресс и стремиться к новым результатам.")


def get_menu(u_id):
    """
    Функция возвращает меню если пользователь зарегистрирован, иначе предлагает пройти этап регистрации
    Args:
        u_id: Уникальный идентификатор пользователя в телеграм
    Returns: Текст сообщения и меню
    """
    already_exist = [True for t in read_teams() if str(u_id) in t.get("name")]
    if already_exist:
        return "Выберите команду.", menu_keyboard
    return "Пройдите этап регистрации.", registration_ikb


@dp.message(CommandStart())
async def start_command(message: types.Message):
    u_id = str(message.from_user.id)
    if global_Dict_del_msg.get(u_id):
        print("global_Dict_del_msg.get(u_id)", global_Dict_del_msg.get(u_id))
        await bot.delete_message(chat_id=message.chat.id, message_id=global_Dict_del_msg[u_id])
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    sent_msg = await message.answer("Добро пожаловать!\n\n" + DESCRIPTION, reply_markup=registration_ikb)
    global_Dict_del_msg[u_id] = sent_msg.message_id
    write_user_values("global_Dict_del_msg", global_Dict_del_msg)


@dp.message(Command('menu'))
async def menu_command(message: types.Message):
    u_id = str(message.from_user.id)
    if global_Dict_del_msg.get(u_id):
        await bot.delete_message(chat_id=message.chat.id, message_id=global_Dict_del_msg[u_id])
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    text, keyboard = get_menu(message.from_user.id)
    sent_msg = await message.answer(text, reply_markup=keyboard)
    global_Dict_del_msg[u_id] = sent_msg.message_id
    write_user_values("global_Dict_del_msg", global_Dict_del_msg)


@dp.callback_query(F.data == 'menu_inline')
async def menu_command_inline(callback: types.CallbackQuery):
    text, keyboard = get_menu(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=keyboard)
