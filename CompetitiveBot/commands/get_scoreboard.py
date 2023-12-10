import requests
from create import dp
from aiogram import types
from tabulate import tabulate
from keyboards import menu_ikb
from commands.url_requests import CONTESTS_SCOREBOARD_URL_TEMPLATE, read_teams


def append_table(t, t_s, a=None, b=None):

    def in_cycle(tbl):
        name = [t.get("display_name") for t in read_teams() if t.get("id") == row.get('team_id')][0]
        if not name:
            name = "Demo user"
        else:
            name_parts = name.split()
            name = " ".join([name_parts[0]] + [f"{p[0]}." for p in name_parts[1:]])
        tbl.append([str(row.get('rank')) + "  ", name, str(row.get('score').get("num_solved")) + "  "])
        return tbl

    if a and not b:
        for row in t[:a]:
            res = in_cycle(t_s)
    elif b and not a:
        for row in t[b:]:
            res = in_cycle(t_s)
    else:
        for row in t:
            res = in_cycle(t_s)

    return res


@dp.callback_query_handler(text='rating')
async def scoreboard(callback: types.CallbackQuery):
    """
    Функция для получения и вывода рейтинговой таблицы
    """
    response = requests.get(CONTESTS_SCOREBOARD_URL_TEMPLATE)

    if response.status_code == 200:
        result = response.json()
        table_show = []
        table = result.get("rows")

        if len(table) > 10:
            table_show = append_table(table, table_show, a=5)
            table_show.append(["...", "...", "..."])
            table_show = append_table(table, table_show, b=-5)
        else:
            table_show = append_table(table, table_show)

        table_show = f'<pre>{tabulate(table_show, headers=["Место", "Пользователь", "Счёт"], tablefmt="simple")}</pre>'
        await callback.message.edit_text(table_show, reply_markup=menu_ikb, parse_mode="HTML")
    else:
        await callback.message.edit_text('Ошибка при отправке запроса', reply_markup=menu_ikb)