from aiogram import types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from create import dp
from commands.general_func import print_task, navigation, get_page, read_user_values, write_user_values
from commands.url_requests import read_problems, read_teams, read_scoreboard
from keyboards import tasks_navigation, menu_keyboard, level_ikb, menu_inline_b, tn_b2, menu_ikb

globalDict_move = read_user_values("globalDict_move")
globalDict_level = read_user_values("globalDict_level")
globalDict_task = read_user_values("globalDict_task")


def get_team_info_from_table(u_id, scoreboard):
    """
    Функция для получения информации о команде
    Args:
        u_id: Идентификатор пользователя в телеграм
        scoreboard: Рейтинговая таблица

    Returns: Информация о команде
    """

    team_info = {}
    table = scoreboard.get("rows")
    for t in read_teams():
        if "_" in t.get("name") and u_id == t.get("name").split("_")[1]:
            team_info = t

    for t in table:
        if t.get("team_id") == team_info.get("id"):
            return t
    return None


def get_solved_tasks_ids(team_info):
    """
    Функция для получения списка идентификаторов решенных задач
    Args:
        team_info: Информация о команде

    Returns: Список идентификаторов решенных задач
    """

    return [p.get("problem_id") for p in team_info.get("problems") if p.get("solved")]


def get_unsolved_tasks(callback_data, u_id):
    """
    Функция для получения не решенных пользователем задач
    Args:
        callback_data: Данные нажатия кнопки
        u_id: Идентификатор пользователя

    Returns: Массив, который включает сообщение, меню, пустой список задач, если возникла ошибка.
             Иначе возвращается только список нерешенных задач.
    """

    unsolved_tasks = []
    problems = read_problems()
    scoreboard = read_scoreboard()

    if not problems or not scoreboard:
        return ['Ошибка при отправке запроса.', menu_ikb, unsolved_tasks]

    if 'task' not in callback_data:
        globalDict_level[u_id] = callback_data
        write_user_values("globalDict_level", globalDict_level)

    tasks_for_level = [t for t in problems if globalDict_level[u_id] in t.get("label")]
    if not tasks_for_level:
        return ['В данный момент задач нет.\nЗагляните позже.', menu_keyboard, unsolved_tasks]

    team_info = get_team_info_from_table(u_id, scoreboard)
    solved_tasks_ids = get_solved_tasks_ids(team_info)
    unsolved_tasks = [t for t in tasks_for_level if t.get("id") not in solved_tasks_ids]

    if not unsolved_tasks:
        return ['Вы решили все задачи данного уровня!', menu_keyboard, unsolved_tasks]

    return [unsolved_tasks]


@dp.callback_query(F.data == 'tasks')
async def get_level(callback: types.CallbackQuery):
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

    tasks_request_result = get_unsolved_tasks(callback.data, usr_id)
    unsolved_tasks = tasks_request_result[-1]

    if not unsolved_tasks:
        message = tasks_request_result[0]
        keyboard = tasks_request_result[1]
        await callback.message.edit_text(message, reply_markup=keyboard)
        await callback.answer()
    else:

        globalDict_level[usr_id] = callback.data
        write_user_values("globalDict_level", globalDict_level)

        if usr_id not in globalDict_task:
            globalDict_task[usr_id] = unsolved_tasks[0].get('id')
            write_user_values("globalDict_task", globalDict_task)
        else:
            globalDict_task[usr_id] = unsolved_tasks[globalDict_move[usr_id]].get('id')
            write_user_values("globalDict_task", globalDict_task)

        page = get_page(usr_id, globalDict_move, unsolved_tasks)
        page_of_all = f"<b>№</b> {page + 1}/{len(unsolved_tasks)}\n\n"
        message = page_of_all + print_task(unsolved_tasks[globalDict_move[usr_id]])
        await callback.message.edit_text(message, reply_markup=tasks_navigation,
                                         disable_web_page_preview=True)


@dp.callback_query(F.data.in_({'left_task', 'right_task'}))
async def show_tasks_lr(callback: types.CallbackQuery):
    """
    Функция просмотра доступных задач при навигации.
    """
    usr_id = str(callback.from_user.id)
    tasks_request_result = get_unsolved_tasks(callback.data, usr_id)
    unsolved_tasks = tasks_request_result[-1]

    if not unsolved_tasks:
        message = tasks_request_result[0]
        keyboard = tasks_request_result[1]
        await callback.message.edit_text(message, reply_markup=keyboard)
        await callback.answer()
    else:
        page = globalDict_move[usr_id]
        number_tasks = len(unsolved_tasks)

        page_of_all, globalDict_move[usr_id] = navigation(callback.data, page, number_tasks)
        write_user_values("globalDict_move", globalDict_move)

        globalDict_task[usr_id] = unsolved_tasks[globalDict_move[usr_id]].get('id')
        write_user_values("globalDict_task", globalDict_task)

        message = page_of_all + print_task(unsolved_tasks[globalDict_move[usr_id]])
        await callback.message.edit_text(message, reply_markup=tasks_navigation,
                                         disable_web_page_preview=True)


@dp.callback_query(F.data == "more_task")
async def show_more_task(callback: types.CallbackQuery):
    """
    Функция для подробного просмотра данных задачи.
    """

    usr_id = str(callback.from_user.id)
    tasks_request_result = get_unsolved_tasks(callback.data, usr_id)
    unsolved_tasks = tasks_request_result[-1]

    if not unsolved_tasks:
        message = tasks_request_result[0]
        keyboard = tasks_request_result[1]
        await callback.message.edit_text(message, reply_markup=keyboard)
        await callback.answer()
    else:
        # Клавиатура при подробном просмотре задачи
        tasks_more_navigation = InlineKeyboardBuilder()
        tmn_b1 = InlineKeyboardButton(text="Вернуться к просмотру",
                                      callback_data=globalDict_level[usr_id])
        tasks_more_navigation = tasks_more_navigation.add(tmn_b1, tn_b2, menu_inline_b)
        tasks_more_navigation = tasks_more_navigation.adjust(1).as_markup()
        message = print_task(unsolved_tasks[globalDict_move[usr_id]], 1)

        await callback.message.edit_text(message, reply_markup=tasks_more_navigation,
                                         disable_web_page_preview=True)
