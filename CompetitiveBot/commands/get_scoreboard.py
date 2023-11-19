import requests
from commands.submit_solution import read_languages
from create import dp
from aiogram import types
from keyboards import menu_ikb


@dp.callback_query_handler(text='rating')
async def scoreboard(callback: types.CallbackQuery):
    """
    Функция для получения рейтинговой таблицы
    """
    url = "http://localhost:12345/api/v4/contests/2/scoreboard?public=true&strict=false"
    response = requests.get(url)
    result = response.json()

    if response.status_code == 200:
        for k, v in result.items():
            print(k, v)
    else:
        await callback.message.edit_text('Ошибка при отправке запроса', reply_markup=menu_ikb)