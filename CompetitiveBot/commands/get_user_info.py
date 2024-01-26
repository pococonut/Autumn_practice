from commands.general_func import get_lvl_task
from commands.get_tasks import print_task, navigation
from commands.url_requests import CONTESTS_SCOREBOARD_URL_TEMPLATE, read_teams, read_problems, read_submissions, \
    read_submission_source_code
from create import dp
from aiogram import types
import requests
from keyboards import menu_ikb, user_info_ikb, solved_tasks_nav, after_result_ikb

globalDict_solved = dict()
globalDict_move_solved = dict()


@dp.callback_query_handler(text='info')
async def user_info(callback: types.CallbackQuery):
    response = requests.get(CONTESTS_SCOREBOARD_URL_TEMPLATE)

    if response.status_code != 200:
        await callback.message.edit_text(f'Ошибка при отправке запроса.', reply_markup=menu_ikb,)
    else:
        result = response.json()
        table = result.get("rows")
        team_info = None
        for t in read_teams():
            if "_" in t.get("name") and str(callback.from_user.id) == t.get("name").split("_")[1]:
                team_info = t

        info = [t for t in table if t.get("team_id") == team_info.get("id")][0]
        solved_problems = [p for p in info.get("problems") if p.get("solved")]

        all_problems = read_problems()

        message_problems = ""
        for sp in solved_problems[:6]:
            task_name = "".join([t.get("name") for t in all_problems if t.get("id") == sp.get("problem_id")])
            level = get_lvl_task(sp)
            message_problems += (f"Задача: {task_name}\n"
                                 f"Уровень: {level}\n"
                                 f"Решил первым: {'Да' if sp.get('first_to_solve') else 'Нет'}\n\n")

        if len(solved_problems) > 5:
            message_problems += "..."

        best_ranks = {"1": "🥇",
                      "2": "🥈",
                      "3": "🥉"}

        line = "-------------------------------\n\n"
        rank = str(info.get('rank'))
        message_info = (f"<b><em>{team_info.get('display_name')}</em></b>\n\n"
                        f"<em>Рейтинг</em>: {rank} место {best_ranks.get(rank) if int(rank) <= 3 else ''}\n"
                        f"<em>Счёт</em>: {info.get('score').get('num_solved')}\n"
                        f"<em>Решённые задачи</em>: {len(solved_problems)}\n\n")
                        # f"{line + message_problems if message_problems else message_problems}\n")

        await callback.message.edit_text(message_info, reply_markup=user_info_ikb, parse_mode="HTML")


@dp.callback_query_handler(text=['solved_tasks', 'left_s', 'right_s'])
async def show_solved_tasks(callback: types.CallbackQuery):
    """
    Функция просмотра решенных задач.
    """
    usr_id = str(callback.from_user.id)
    if usr_id not in globalDict_move_solved:
        globalDict_move_solved[usr_id] = 0

    solved_problems = []
    response = requests.get(CONTESTS_SCOREBOARD_URL_TEMPLATE)
    if response.status_code != 200:
        await callback.message.edit_text(f'Ошибка при отправке запроса.', reply_markup=menu_ikb, )
    else:
        result = response.json()
        table = result.get("rows")
        team_info = None
        for t in read_teams():
            if "_" in t.get("name") and str(callback.from_user.id) == t.get("name").split("_")[1]:
                team_info = t

        info = [t for t in table if t.get("team_id") == team_info.get("id")][0]
        solved_problems = [p.get("problem_id") for p in info.get("problems") if p.get("solved")]

    all_tasks = read_problems()
    solved_problems = [t for t in all_tasks if t.get("id") in solved_problems]
    print(solved_problems)
    if not solved_problems:
        await callback.message.edit_text(f'У вас нет решенных задач.', reply_markup=menu_ikb)
    else:

        if usr_id not in globalDict_solved:
            globalDict_solved[usr_id] = solved_problems[0].get('id')

        count_tasks = len(solved_problems)
        if callback.data == "solved_tasks":
            p = globalDict_move_solved[usr_id]
            if globalDict_move_solved[usr_id] <= -1:
                p = count_tasks + globalDict_move_solved[usr_id]
            await callback.message.edit_text(
                f"<b>№</b> {p + 1}/{count_tasks}\n\n" + print_task(solved_problems[globalDict_move_solved[usr_id]]),
                parse_mode='HTML',
                reply_markup=solved_tasks_nav,
                disable_web_page_preview=True)

        elif callback.data in ('left_s', 'right_s'):
            s, globalDict_move_solved[usr_id] = navigation(callback.data, globalDict_move_solved[usr_id], count_tasks)
            globalDict_solved[usr_id] = solved_problems[globalDict_move_solved[usr_id]].get('id')
            await callback.message.edit_text(s + print_task(solved_problems[globalDict_move_solved[usr_id]]),
                                             parse_mode='HTML',
                                             reply_markup=solved_tasks_nav,
                                             disable_web_page_preview=True)

        """if callback.data == "more_task":
            # Клавиатура при подробном просмотре задачи
            tasks_more_navigation = InlineKeyboardMarkup()
            tmn_b1 = InlineKeyboardButton(text="Вернуться к просмотру", callback_data=globalDict_level[usr_id])
            tasks_more_navigation.add(tmn_b1).add(tn_b2).add(menu_inline_b)

            text_task = print_task(tasks[globalDict_move[usr_id]], 1)
            await callback.message.edit_text(text_task,
                                             parse_mode='HTML',
                                             reply_markup=tasks_more_navigation,
                                             disable_web_page_preview=True)"""


@dp.callback_query_handler(text="code_source")
async def show_task_code(callback: types.CallbackQuery):
    """
    Функция вывода исходного кода решения
    """

    submission = [s for s in read_submissions() if s["problem_id"] == globalDict_solved[str(callback.from_user.id)]]
    code_source = f"<code>{read_submission_source_code(submission[0].get('id'))}</code>"
    await callback.message.edit_text(code_source, reply_markup=after_result_ikb, parse_mode='HTML')