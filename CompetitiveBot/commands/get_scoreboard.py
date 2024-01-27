from create import dp
from aiogram import types
from tabulate import tabulate
from keyboards import menu_ikb
from commands.url_requests import read_teams, read_scoreboard


def append_table(data, tbl_show, a=None, b=None):
    """
    Функция для заполнения рейтинговой таблицы данными
    Args:
        data: Данные рейтинговой таблицы
        tbl_show: Таблица для заполнения и вывода
        a: Срез [a:]
        b: Срез [:b]
    Returns: Заполненная данными таблица
    """

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
        for row in data[:a]:
            res = in_cycle(tbl_show)
    elif b and not a:
        for row in data[b:]:
            res = in_cycle(tbl_show)
    else:
        for row in data:
            res = in_cycle(tbl_show)
    return res


@dp.callback_query_handler(text='rating')
async def show_scoreboard(callback: types.CallbackQuery):
    """
    Функция для получения и вывода рейтинговой таблицы
    """

    scoreboard = read_scoreboard()
    if scoreboard:
        table_show = []
        scoreboard_data = scoreboard.get("rows")

        if len(scoreboard_data) > 10:
            table_show = append_table(scoreboard_data, table_show, a=5)
            table_show.append(["...", "...", "..."])
            table_show = append_table(scoreboard_data, table_show, b=-5)
        else:
            table_show = append_table(scoreboard_data, table_show)

        table_show = f'<pre>{tabulate(table_show, headers=["Место", "Пользователь", "Счёт"], tablefmt="simple")}</pre>'
        await callback.message.edit_text(table_show, reply_markup=menu_ikb, parse_mode="HTML")
    else:
        await callback.message.edit_text('Ошибка при отправке запроса', reply_markup=menu_ikb)