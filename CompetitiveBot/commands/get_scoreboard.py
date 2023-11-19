import requests
from config import settings
from create import dp
from aiogram import types
from keyboards import menu_ikb
from tabulate import tabulate


@dp.callback_query_handler(text='rating')
async def scoreboard(callback: types.CallbackQuery):
    """
    Функция для получения рейтинговой таблицы
    """
    url = "http://localhost:12345/api/v4/contests/2/scoreboard?public=true&strict=false"
    response = requests.get(url)
    result = response.json()

    if response.status_code == 200:

        table_show = []
        table = result.get("rows")

        username = settings.admin_username
        password = settings.admin_password
        session = requests.Session()
        session.auth = (username, password)
        url_get_teams = "http://localhost:12345/api/v4/contests/2/teams?strict=false"
        response_get_teams = session.get(url_get_teams).json()
        for row in table:
            name = [t.get("display_name") for t in response_get_teams if t.get("id") == row.get('team_id')][0]
            if not name:
                name = "Demo user"

            table_show.append([row.get('rank'), name, row.get('score').get("num_solved")])
        table_show = f'<pre>{tabulate(table_show, headers=["Место", "Пользователь", "Счёт"], tablefmt="simple_grid")}</pre>'
        await callback.message.edit_text(table_show, reply_markup=menu_ikb, parse_mode="HTML")
    else:
        await callback.message.edit_text('Ошибка при отправке запроса', reply_markup=menu_ikb)