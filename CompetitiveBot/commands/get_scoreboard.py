from aiogram import types, F
from tabulate import tabulate
from create import dp
from keyboards import menu_ikb
from commands.url_requests import read_teams, read_scoreboard


def add_beautiful_row(table, row):
    """
    Функция для формирования строки таблицы и ее заполнения
    Args:
        table: Таблица
        row: Строка

    Returns: Заполненная новой строкой таблица
    """

    name = None
    for team in read_teams():
        if team.get("id") == row.get('team_id'):
            name = team.get("display_name")

    if not name:
        name = "Demo user"
    else:
        name_parts = name.split()
        surname = name_parts[0]
        initials = " ".join([f"{p[0]}." for p in name_parts[1:]])
        name = surname + " " + initials

    rank = str(row.get('rank'))
    score = str(row.get('score').get("num_solved"))
    row = [rank + "  ", name, score + "  "]
    table.append(row)

    return table


def append_table(table_data, tbl_show, first_five=None, last_five=None):
    """
    Функция для заполнения рейтинговой таблицы данными
    Args:
        table_data: Данные рейтинговой таблицы
        tbl_show: Таблица для заполнения и вывода
        first_five: Срез [first_five:]
        last_five: Срез [:last_five]

    Returns: Заполненная данными таблица
    """

    table = ""

    if not first_five and not last_five:
        for data in table_data:
            table = add_beautiful_row(tbl_show, data)
    elif first_five:
        for data in table_data[:first_five]:
            table = add_beautiful_row(tbl_show, data)
    elif last_five:
        for data in table_data[last_five:]:
            table = add_beautiful_row(tbl_show, data)

    return table


@dp.callback_query(F.data == 'rating')
async def show_scoreboard(callback: types.CallbackQuery):
    """
    Функция для получения и вывода рейтинговой таблицы
    """

    scoreboard = read_scoreboard()
    if not scoreboard:
        table = 'Ошибка при отправке запроса'
        await callback.message.edit_text(table, reply_markup=menu_ikb)
        return

    table = []
    scoreboard_data = scoreboard.get("rows")

    if len(scoreboard_data) > 10:
        table = append_table(scoreboard_data, table, first_five=5)
        table.append(["...", "...", "..."])
        table = append_table(scoreboard_data, table, last_five=-5)
    else:
        table = append_table(scoreboard_data, table)

    table_header = ["Место", "Пользователь", "Счёт"]
    table = f'<pre>{tabulate(table, headers=table_header, tablefmt="simple")}</pre>'

    await callback.message.edit_text(table, reply_markup=menu_ikb)
