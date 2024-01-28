from create import dp
from aiogram import types
from keyboards import menu_ikb
from commands.url_requests import read_languages


@dp.callback_query_handler(text='lang')
async def languages(callback: types.CallbackQuery):
    """
    Функция для получения списка доступных языков программирования
    """

    result = read_languages()
    if result:
        available_lang = "\n▫️ ".join([i['name'] for i in result])
        await callback.message.edit_text(f'Решения принимаются на языках:\n▫️ {available_lang}', reply_markup=menu_ikb)
    else:
        await callback.message.edit_text('Ошибка при отправке запроса', reply_markup=menu_ikb)
