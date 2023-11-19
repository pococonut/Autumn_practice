import requests
from create import dp
from aiogram import types
from tabulate import tabulate
from keyboards import menu_ikb
from commands.url_requests import CONTESTS_SCOREBOARD_URL_TEMPLATE, read_teams


@dp.callback_query_handler(text='rating')
async def scoreboard(callback: types.CallbackQuery):
    """
    Функция для получения рейтинговой таблицы
    """
    response = requests.get(CONTESTS_SCOREBOARD_URL_TEMPLATE)
    result = response.json()

    if response.status_code == 200:
        table_show = []
        table = result.get("rows")
        for row in table:
            name = [t.get("display_name") for t in read_teams() if t.get("id") == row.get('team_id')][0]
            if not name:
                name = "Demo user"
            table_show.append([row.get('rank'), name, row.get('score').get("num_solved")])

        table_show = f'<pre>{tabulate(table_show, headers=["Место", "Пользователь", "Счёт"], tablefmt="simple_grid")}</pre>'
        await callback.message.edit_text(table_show, reply_markup=menu_ikb, parse_mode="HTML")
    else:
        await callback.message.edit_text('Ошибка при отправке запроса', reply_markup=menu_ikb)