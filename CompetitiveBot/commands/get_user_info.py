from create import dp
from aiogram import types
from commands.general_func import print_task, navigation
from keyboards import menu_ikb, user_info_ikb, solved_tasks_nav, source_code_ikb
from commands.url_requests import read_teams, read_problems, read_submissions, read_submission_source_code, read_scoreboard

globalDict_solved = dict()
globalDict_move_solved = dict()


@dp.callback_query_handler(text='info')
async def user_info(callback: types.CallbackQuery):
    scoreboard = read_scoreboard()

    if not scoreboard:
        await callback.message.edit_text(f'Ошибка при отправке запроса.', reply_markup=menu_ikb,)
    else:
        best_ranks = {"1": "🥇",
                      "2": "🥈",
                      "3": "🥉"}

        table = scoreboard.get("rows")
        team_info = None
        for t in read_teams():
            if "_" in t.get("name") and str(callback.from_user.id) == t.get("name").split("_")[1]:
                team_info = t

        info = [t for t in table if t.get("team_id") == team_info.get("id")][0]
        solved_problems = [p for p in info.get("problems") if p.get("solved")]

        rank = str(info.get('rank'))
        message_info = (f"<b><em>{team_info.get('display_name')}</em></b>\n\n"
                        f"<em>Рейтинг</em>: {rank} место {best_ranks.get(rank) if int(rank) <= 3 else ''}\n"
                        f"<em>Счёт</em>: {info.get('score').get('num_solved')}\n"
                        f"<em>Решённые задачи</em>: {len(solved_problems)}\n\n")

        await callback.message.edit_text(message_info, reply_markup=user_info_ikb, parse_mode="HTML")


@dp.callback_query_handler(text=['solved_tasks', 'left_s', 'right_s'])
async def show_solved_tasks(callback: types.CallbackQuery):
    """
    Функция просмотра решенных задач.
    """
    usr_id = str(callback.from_user.id)
    if usr_id not in globalDict_move_solved:
        globalDict_move_solved[usr_id] = 0

    solved_idx = []
    solved_problems = []
    scoreboard = read_scoreboard()

    if not scoreboard:
        await callback.message.edit_text(f'Ошибка при отправке запроса.', reply_markup=menu_ikb, )
    else:
        table = scoreboard.get("rows")
        team_info = None
        for t in read_teams():
            if "_" in t.get("name") and str(callback.from_user.id) == t.get("name").split("_")[1]:
                team_info = t

        info = [t for t in table if t.get("team_id") == team_info.get("id")][0]
        solved_idx = dict((p.get("problem_id"), p.get("first_to_solve")) for p in info.get("problems") if p.get("solved"))

    for t in read_problems():
        if t.get("id") in solved_idx:
            t["first_to_solve"] = solved_idx.get(t.get("id"))
            solved_problems.append(t)

    if not solved_problems:
        await callback.message.edit_text(f'У вас нет решенных задач.', reply_markup=menu_ikb)
    else:
        count_tasks = len(solved_problems)
        if usr_id not in globalDict_solved:
            globalDict_solved[usr_id] = solved_problems[0].get('id')

        if callback.data == "solved_tasks":
            p = globalDict_move_solved[usr_id]
            if globalDict_move_solved[usr_id] <= -1:
                p = count_tasks + globalDict_move_solved[usr_id]

            current_page = solved_problems[globalDict_move_solved[usr_id]]
            first_solution = f"\n\n<b>Решил первым</b>: {'Да' if current_page.get('first_to_solve') else 'Нет'}\n\n"

            await callback.message.edit_text(
                f"<b>№</b> {p + 1}/{count_tasks}\n\n" + print_task(current_page) + first_solution, parse_mode='HTML',
                reply_markup=solved_tasks_nav,
                disable_web_page_preview=True)

        elif callback.data in ('left_s', 'right_s'):
            current_page = solved_problems[globalDict_move_solved[usr_id]]
            first_solution = f"\n\n<b>Решил первым</b>: {'Да' if current_page.get('first_to_solve') else 'Нет'}\n\n"

            s, globalDict_move_solved[usr_id] = navigation(callback.data, globalDict_move_solved[usr_id], count_tasks)
            globalDict_solved[usr_id] = current_page.get('id')
            await callback.message.edit_text(s + print_task(current_page) + first_solution, parse_mode='HTML',
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