from create import dp
from aiogram import types, F
from commands.general_func import print_task, navigation, get_page, read_user_values, write_user_values
from commands.url_requests import read_problems, read_teams, read_scoreboard
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from keyboards import tasks_navigation, menu_keyboard, level_ikb, menu_inline_b, tn_b2, menu_ikb

globalDict_move = read_user_values("globalDict_move")
globalDict_level = read_user_values("globalDict_level")
globalDict_task = read_user_values("globalDict_task")


def get_unsolved_tasks(callback_data, u_id):
    """
    Функция для получения не решенных пользователем задач
    Args:
        callback_data: Данные нажатия кнопки
        u_id: Идентификатор пользователя

    Returns: Массив, который включает сообщение, меню, пустой список задач, если возникла ошибка.
             Иначе возвращается только список нерешенных задач.
    """

    tasks = []
    problems = read_problems()
    scoreboard = read_scoreboard()

    if not problems or not scoreboard:
        return ['Ошибка при отправке запроса.', menu_ikb, tasks]

    if 'task' not in callback_data:
        globalDict_level[u_id] = callback_data
        write_user_values("globalDict_level", globalDict_level)

    all_tasks = [t for t in problems if globalDict_level[u_id] in t.get("label")]
    if not all_tasks:
        return ['В данный момент задач нет.\nЗагляните позже.', menu_keyboard, tasks]

    team_info = dict()
    table = scoreboard.get("rows")
    for t in read_teams():
        if "_" in t.get("name") and u_id == t.get("name").split("_")[1]:
            team_info = t

    u_info = [t for t in table if t.get("team_id") == team_info.get("id")][0]
    solved_tasks_ids = [p.get("problem_id") for p in u_info.get("problems") if p.get("solved")]
    tasks = [t for t in all_tasks if t.get("id") not in solved_tasks_ids]
    if not tasks:
        return ['Вы решили все задачи данного уровня!', menu_keyboard, tasks]

    return [tasks]


@dp.callback_query(F.data == 'tasks')
async def get_lvl(callback: types.CallbackQuery):
    """
    Функция выбора сложности задач.
    """

    await callback.message.edit_text("Выберите уровень сложности.", reply_markup=level_ikb)
    globalDict_move[str(callback.from_user.id)] = 0
    write_user_values("globalDict_move", globalDict_move)


@dp.callback_query(F.data.in_({'A', 'B', 'C'}))
async def show_tasks(callback: types.CallbackQuery):
    """
    Функция просмотра доступных задач.
    """

    usr_id = str(callback.from_user.id)
    if usr_id not in globalDict_move:
        globalDict_move[usr_id] = 0
        write_user_values("globalDict_move", globalDict_move)

    tasks_lst = get_unsolved_tasks(callback.data, usr_id)
    if not tasks_lst[-1]:
        await callback.message.edit_text(tasks_lst[0], reply_markup=tasks_lst[1])
        await callback.answer()
    else:
        tasks = tasks_lst[-1]
        globalDict_level[usr_id] = callback.data
        write_user_values("globalDict_level", globalDict_level)

        if usr_id not in globalDict_task:
            globalDict_task[usr_id] = tasks[0].get('id')
            write_user_values("globalDict_task", globalDict_task)
        else:
            globalDict_task[usr_id] = tasks[globalDict_move[usr_id]].get('id')
            write_user_values("globalDict_task", globalDict_task)
        p = get_page(usr_id, globalDict_move, tasks)
        s = f"<b>№</b> {p + 1}/{len(tasks)}\n\n"
        await callback.message.edit_text(s + print_task(tasks[globalDict_move[usr_id]]), reply_markup=tasks_navigation,
                                         disable_web_page_preview=True)


@dp.callback_query(F.data.in_({'left_task', 'right_task'}))
async def show_tasks_lr(callback: types.CallbackQuery):
    """
    Функция просмотра доступных задач при навигации.
    """
    usr_id = str(callback.from_user.id)
    tasks_lst = get_unsolved_tasks(callback.data, usr_id)

    if not tasks_lst[-1]:
        await callback.message.edit_text(tasks_lst[0], reply_markup=tasks_lst[1])
        await callback.answer()
    else:
        tasks = tasks_lst[-1]
        s, globalDict_move[usr_id] = navigation(callback.data, globalDict_move[usr_id], len(tasks))
        write_user_values("globalDict_move", globalDict_move)

        globalDict_task[usr_id] = tasks[globalDict_move[usr_id]].get('id')
        write_user_values("globalDict_task", globalDict_task)
        await callback.message.edit_text(s + print_task(tasks[globalDict_move[usr_id]]), reply_markup=tasks_navigation,
                                         disable_web_page_preview=True)


@dp.callback_query(F.data == "more_task")
async def show_more_task(callback: types.CallbackQuery):
    """
    Функция для подробного просмотра данных задачи.
    """

    usr_id = str(callback.from_user.id)
    tasks_lst = get_unsolved_tasks(callback.data, usr_id)
    if not tasks_lst[-1]:
        await callback.message.edit_text(tasks_lst[0], reply_markup=tasks_lst[1])
        await callback.answer()

    # Клавиатура при подробном просмотре задачи
    tasks_more_navigation = InlineKeyboardBuilder()
    tmn_b1 = InlineKeyboardButton(text="Вернуться к просмотру", callback_data=globalDict_level[usr_id])
    tasks_more_navigation = tasks_more_navigation.add(tmn_b1, tn_b2, menu_inline_b).adjust(1).as_markup()
    text_task = print_task(tasks_lst[-1][globalDict_move[usr_id]], 1)

    await callback.message.edit_text(text_task, reply_markup=tasks_more_navigation, disable_web_page_preview=True)
