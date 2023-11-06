import requests

from commands.submit_solution import read_languages
from create import dp
from aiogram import types
from keyboards import menu_keyboard


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
        await callback.message.edit_text(f'Решения принимаются на языках:\n▫️ {available_lang}', reply_markup=menu_keyboard,)
    else:
        await callback.message.edit_text('Ошибка при отправке запроса', reply_markup=menu_keyboard)

"""    contest_id = '2'
    username = 'demo'
    password = '1234567890'
    baseurl = 'http://localhost:12345/'
    api_version = 'v4'

    headers = {'user-agent': f'domjudge-submit-client ({requests.utils.default_user_agent()})'}
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers['Authorization'] = f'Basic {credentials}'

    read_languages(baseurl, api_version, headers, contest_id)"""
