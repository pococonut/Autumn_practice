import requests
from create import dp
from aiogram import types
from keyboards import menu


@dp.callback_query_handler(text='lang')
async def languages(callback: types.CallbackQuery):
    """
    Функция для получения списка доступных языков программирования
    """
    url = 'http://localhost:12345/api/v4/languages?strict=false'
    response = requests.get(url)
    result = response.json()

    if response.status_code == 200:
        available_lang = "\n▫️ ".join([i['name'] for i in result])
        await callback.message.edit_text(f'Решения принимаются на языках:\n▫️ {available_lang}', reply_markup=menu,)
    else:
        await callback.message.edit_text('Ошибка при отправке запроса', reply_markup=menu)
