from aiogram import types, F
from create import dp
from keyboards import menu_ikb, user_info_ikb, solved_tasks_nav, source_code_ikb
from commands.get_tasks import get_team_info_from_table
from commands.general_func import print_task, navigation, get_page, read_user_values, write_user_values
from commands.url_requests import read_teams, read_problems, read_submissions, read_submission_source_code, \
    read_scoreboard

globalDict_solved = read_user_values("globalDict_solved")
globalDict_move_solved = read_user_values("globalDict_move_solved")


def get_solved_tasks_ids_with_first(team_info):
    """
    Функция для получения списка идентификаторов
    решенных задач с параметром "Решил первым - Да/Нет"
    Args:
        team_info: Информация о команде

    Returns: Список идентификаторов решенных
     задач с параметром "Решил первым - Да/Нет"
    """

    return dict((p.get("problem_id"), p.get("first_to_solve")) for p in team_info.get("problems") if p.get("solved"))


def get_solved_tasks(usr_id):
    """
    Функция для получения решенных пользователем задач
    Args:
        usr_id: Идентификатор пользователя

    Returns: Массив, который включает сообщение, меню, пустой список задач, если возникла ошибка.
             Иначе возвращается только список нерешенных задач.
    """

    if usr_id not in globalDict_move_solved:
        globalDict_move_solved[usr_id] = 0
        write_user_values("globalDict_move_solved", globalDict_move_solved)

    solved_problems = []
    problems = read_problems()
    scoreboard = read_scoreboard()

    if not problems or not scoreboard:
        return ['Ошибка при отправке запроса.', menu_ikb, solved_problems]

    team_info = get_team_info_from_table(usr_id, scoreboard)
    solved_tasks_ids = get_solved_tasks_ids_with_first(team_info)

    for problem in problems:
        if problem.get("id") in solved_tasks_ids:
            problem["first_to_solve"] = solved_tasks_ids.get(problem.get("id"))
            solved_problems.append(problem)

    if not solved_problems:
        return ['У вас нет решенных задач.', menu_ikb, solved_problems]

    return [solved_problems]


def get_usr_rating_info(team_info, scoreboard):
    """
    Функция для получения информации о команде из рейтинговой таблицы
    Args:
        team_info: Информация о команде
        scoreboard: Рейтинговая таблица

    Returns: Информация о команде из рейтинговой таблицы
    """

    for team in scoreboard.get("rows"):
        if team.get("team_id") == team_info.get("id"):
            return team


def get_team_info(usr_id):
    """
    Функция для получения информации о команде
    Args:
        usr_id: Идентификатор пользователя в телеграм

    Returns: Информация о команде
    """

    for team in read_teams():
        if "_" in team.get("name") and usr_id == team.get("name").split("_")[1]:
            return team


def first_or_not(curr_problem):
    """
    Функция для определения, решил ли пользователь
    текущую задачу первым из всех пользователей
    Args:
        curr_problem: Текущая задача

    Returns: Строка с ответом
    """

    return f"\n\n<b>Решил первым</b>: {'Да' if curr_problem.get('first_to_solve') else 'Нет'}\n\n"


def get_current_submission(usr_id):
    """
    Функция для получения информации о текущем решении
    Args:
        usr_id: Идентификатор пользователя в телеграм

    Returns: Информация о текущем решении
    """

    for s in read_submissions():
        if s["problem_id"] == globalDict_solved[usr_id]:
            return s


@dp.callback_query(F.data == 'info')
async def user_info(callback: types.CallbackQuery):
    """
    Функция для просмотра личной информации пользователя.
    """

    scoreboard = read_scoreboard()
    if not scoreboard:
        await callback.message.edit_text(f'Ошибка при отправке запроса.', reply_markup=menu_ikb)
    else:
        usr_id = str(callback.from_user.id)

        team_info = get_team_info(usr_id)
        rating_usr_info = get_usr_rating_info(team_info, scoreboard)
        solved_problems = [p for p in rating_usr_info.get("problems") if p.get("solved")]
        best_ranks = {"1": "🥇", "2": "🥈", "3": "🥉"}

        user_name = team_info.get('display_name')
        rank = str(rating_usr_info.get('rank'))
        rank_emoji = best_ranks.get(rank) if int(rank) <= 3 else ''
        score = rating_usr_info.get('score').get('num_solved')

        message_info = (f"<b><em>{user_name}</em></b>\n\n"
                        f"<em>Рейтинг</em>: {rank} место {rank_emoji}\n"
                        f"<em>Счёт</em>: {score}\n"
                        f"<em>Решённые задачи</em>: {len(solved_problems)}\n\n")

        await callback.message.edit_text(message_info, reply_markup=user_info_ikb)


@dp.callback_query(F.data == 'solved_tasks')
async def show_solved_tasks(callback: types.CallbackQuery):
    """
    Функция для просмотра решенных задач.
    """

    usr_id = str(callback.from_user.id)
    tasks_request_result = get_solved_tasks(usr_id)
    solved_tasks = tasks_request_result[-1]

    if not solved_tasks:
        message = tasks_request_result[0]
        keyboard = tasks_request_result[1]
        await callback.message.edit_text(message, reply_markup=keyboard)
    else:

        if usr_id not in globalDict_solved:
            globalDict_solved[usr_id] = solved_tasks[0].get('id')
            write_user_values("globalDict_solved", globalDict_solved)
        else:
            globalDict_solved[usr_id] = solved_tasks[globalDict_move_solved[usr_id]].get('id')
            write_user_values("globalDict_solved", globalDict_solved)

        page = get_page(usr_id, globalDict_move_solved, solved_tasks)
        page_of_all = f"<b>№</b> {page + 1}/{len(solved_tasks)}\n\n"
        curr_problem = solved_tasks[globalDict_move_solved[usr_id]]
        first_solution = first_or_not(curr_problem)
        message = page_of_all + print_task(curr_problem) + first_solution

        await callback.message.edit_text(message, reply_markup=solved_tasks_nav,
                                         disable_web_page_preview=True)


@dp.callback_query(F.data.in_({'left_s', 'right_s'}))
async def show_solved_tasks_lr(callback: types.CallbackQuery):
    """
    Функция для просмотра решенных задач при навигации.
    """

    usr_id = str(callback.from_user.id)
    tasks_request_result = get_solved_tasks(usr_id)
    solved_tasks = tasks_request_result[-1]

    if not solved_tasks:
        message = tasks_request_result[0]
        keyboard = tasks_request_result[1]
        await callback.message.edit_text(message, reply_markup=keyboard)
    else:
        page = globalDict_move_solved[usr_id]
        number_tasks = len(solved_tasks)

        page_of_all, globalDict_move_solved[usr_id] = navigation(callback.data, page, number_tasks)
        write_user_values("globalDict_move_solved", globalDict_move_solved)

        curr_problem = solved_tasks[globalDict_move_solved[usr_id]]
        first_solution = first_or_not(curr_problem)
        globalDict_solved[usr_id] = curr_problem.get('id')
        write_user_values("globalDict_solved", globalDict_solved)
        message = page_of_all + print_task(curr_problem) + first_solution

        await callback.message.edit_text(message, reply_markup=solved_tasks_nav,
                                         disable_web_page_preview=True)


@dp.callback_query(F.data == "code_source")
async def show_task_code(callback: types.CallbackQuery):
    """
    Функция для вывода исходного кода решения
    """

    usr_id = str(callback.from_user.id)
    submission = get_current_submission(usr_id)
    code_source = f"<code>{read_submission_source_code(submission.get('id'))}</code>"
    await callback.message.edit_text(code_source, reply_markup=source_code_ikb)
