import logging
from aiogram import types, F
from aiogram.filters.command import Command, CommandStart
from create import dp, bot
from commands.url_requests import read_teams
from commands.general_func import read_user_values, write_user_values
from keyboards import menu_keyboard, registration_ikb


global_Dict_del_msg = read_user_values("global_Dict_del_msg")

DESCRIPTION = ("Телеграм бот предоставляет список доступных задач по программированию "
               "трех уровней сложности. Решения принимаются на нескольких доступных языках, "
               "благодаря чему, вы можете проверить свои навыки в каждом из них.\n\n"
               "Также бот выводит рейтинговую таблицу, где вы можете увидеть свое "
               "место среди других пользователей. Это поможет вам отслеживать свой прогресс "
               "и стремиться к новым результатам.")


def get_menu(usr_id):
    """
    Функция возвращает меню если пользователь зарегистрирован,
    иначе предлагает пройти этап регистрации
    Args:
        usr_id: Уникальный идентификатор пользователя в телеграм
    Returns: Текст сообщения и меню
    """

    try:
        for team in read_teams():
            if usr_id in team.get("name"):
                return "Выберите команду.", menu_keyboard
    except:
        return "Пройдите этап регистрации.", registration_ikb

    return "Пройдите этап регистрации.", registration_ikb


@dp.message(CommandStart())
async def start_command(message: types.Message):
    """
    Функция вывода приветственного сообщения и начала взаимодействия с телеграм-ботом
    """

    usr_id = str(message.from_user.id)
    if global_Dict_del_msg.get(usr_id):
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=global_Dict_del_msg[usr_id])
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except Exception as e:
            logging.exception(e)

    sent_msg = await message.answer("Добро пожаловать!\n\n" + DESCRIPTION, reply_markup=registration_ikb)
    global_Dict_del_msg[usr_id] = sent_msg.message_id
    write_user_values("global_Dict_del_msg", global_Dict_del_msg)


@dp.message(Command('menu'))
async def menu_command(message: types.Message):
    """
    Функция вызова меню
    """

    usr_id = str(message.from_user.id)
    if global_Dict_del_msg.get(usr_id):
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=global_Dict_del_msg[usr_id])
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except Exception as e:
            logging.exception(e)

    text, keyboard = get_menu(usr_id)
    sent_msg = await message.answer(text, reply_markup=keyboard)
    global_Dict_del_msg[usr_id] = sent_msg.message_id
    write_user_values("global_Dict_del_msg", global_Dict_del_msg)


@dp.callback_query(F.data == 'menu_inline')
async def menu_command_inline(callback: types.CallbackQuery):
    """
    Функция вызова inline меню
    """

    text, keyboard = get_menu(str(callback.from_user.id))
    await callback.message.edit_text(text, reply_markup=keyboard)
