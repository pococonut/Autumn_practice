from create import dp
from aiogram import types
from commands.general_func import print_task, navigation, get_page
from keyboards import menu_ikb, user_info_ikb, solved_tasks_nav, source_code_ikb
from commands.url_requests import read_teams, read_problems, read_submissions, read_submission_source_code, \
    read_scoreboard

globalDict_solved = dict()
globalDict_move_solved = dict()


def get_solved_tasks(u_id):
    """
    Функция для получения решенных пользователем задач
    Args:
        u_id: Идентификатор пользователя

    Returns: Массив, который включает сообщение, меню, пустой список задач, если возникла ошибка.
             Иначе возвращается только список нерешенных задач.
    """

    solved_problems = []
    if u_id not in globalDict_move_solved:
        globalDict_move_solved[u_id] = 0

    if not read_scoreboard():
        return ['Ошибка при отправке запроса.', menu_ikb, solved_problems]
    else:
        team_info = dict()
        for t in read_teams():
            if "_" in t.get("name") and u_id == t.get("name").split("_")[1]:
                team_info = t

        info = [t for t in read_scoreboard().get("rows") if t.get("team_id") == team_info.get("id")][0]
        s_idx = dict((p.get("problem_id"), p.get("first_to_solve")) for p in info.get("problems") if p.get("solved"))

    for t in read_problems():
        if t.get("id") in s_idx:
            t["first_to_solve"] = s_idx.get(t.get("id"))
            solved_problems.append(t)

    if not solved_problems:
        return ['У вас нет решенных задач.', menu_ikb, solved_problems]

    return [solved_problems]


@dp.callback_query_handler(text='info')
async def user_info(callback: types.CallbackQuery):
    """
    Функция для просмотра личной информации пользователя.
    """
    if not read_scoreboard():
        await callback.message.edit_text(f'Ошибка при отправке запроса.', reply_markup=menu_ikb, )
    else:
        team_info = dict()
        for t in read_teams():
            if "_" in t.get("name") and str(callback.from_user.id) == t.get("name").split("_")[1]:
                team_info = t

        info = [t for t in read_scoreboard().get("rows") if t.get("team_id") == team_info.get("id")][0]
        solved_problems = [p for p in info.get("problems") if p.get("solved")]
        best_ranks = {"1": "🥇", "2": "🥈", "3": "🥉"}
        rank = str(info.get('rank'))

        message_info = (f"<b><em>{team_info.get('display_name')}</em></b>\n\n"
                        f"<em>Рейтинг</em>: {rank} место {best_ranks.get(rank) if int(rank) <= 3 else ''}\n"
                        f"<em>Счёт</em>: {info.get('score').get('num_solved')}\n"
                        f"<em>Решённые задачи</em>: {len(solved_problems)}\n\n")

        await callback.message.edit_text(message_info, reply_markup=user_info_ikb, parse_mode="HTML")


@dp.callback_query_handler(text='solved_tasks')
async def show_solved_tasks(callback: types.CallbackQuery):
    """
    Функция просмотра решенных задач.
    """

    usr_id = str(callback.from_user.id)
    s_problems_lst = get_solved_tasks(usr_id)

    if not s_problems_lst[-1]:
        await callback.message.edit_text(s_problems_lst[0], reply_markup=s_problems_lst[1])
    else:
        solved_problems = s_problems_lst[-1]
        p = get_page(usr_id, globalDict_solved, globalDict_move_solved, solved_problems)
        s = f"<b>№</b> {p + 1}/{len(solved_problems)}\n\n"
        curr_problem = solved_problems[globalDict_move_solved[usr_id]]
        first_solution = f"\n\n<b>Решил первым</b>: {'Да' if curr_problem.get('first_to_solve') else 'Нет'}\n\n"

        await callback.message.edit_text(s + print_task(curr_problem) + first_solution, parse_mode='HTML',
                                         reply_markup=solved_tasks_nav,
                                         disable_web_page_preview=True)


@dp.callback_query_handler(text=['left_s', 'right_s'])
async def show_solved_tasks_lr(callback: types.CallbackQuery):
    """
    Функция просмотра решенных задач при навигации.
    """

    usr_id = str(callback.from_user.id)
    s_problems_lst = get_solved_tasks(usr_id)

    if not s_problems_lst[-1]:
        await callback.message.edit_text(s_problems_lst[0], reply_markup=s_problems_lst[1])
    else:
        s_problems = s_problems_lst[-1]
        s, globalDict_move_solved[usr_id] = navigation(callback.data, globalDict_move_solved[usr_id], len(s_problems))
        curr_problem = s_problems[globalDict_move_solved[usr_id]]
        first_solution = f"\n\n<b>Решил первым</b>: {'Да' if curr_problem.get('first_to_solve') else 'Нет'}\n\n"
        globalDict_solved[usr_id] = curr_problem.get('id')

        await callback.message.edit_text(s + print_task(curr_problem) + first_solution, parse_mode='HTML',
                                         reply_markup=solved_tasks_nav,
                                         disable_web_page_preview=True)


@dp.callback_query_handler(text="code_source")
async def show_task_code(callback: types.CallbackQuery):
    """
    Функция вывода исходного кода решения
    """

    submission = [s for s in read_submissions() if s["problem_id"] == globalDict_solved[str(callback.from_user.id)]]
    code_source = f"<code>{read_submission_source_code(submission[0].get('id'))}</code>"
    await callback.message.edit_text(code_source, reply_markup=source_code_ikb, parse_mode='HTML')
