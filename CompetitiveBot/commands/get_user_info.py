from commands.general_func import get_lvl_task
from commands.url_requests import CONTESTS_SCOREBOARD_URL_TEMPLATE, read_teams, read_problems
from create import dp
from aiogram import types
import requests
from keyboards import menu_ikb


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

        rank = str(info.get('rank'))
        message_info = (f"<b><em>{team_info.get('display_name')}</em></b>\n\n"
                        f"<em>Рейтинг</em>: {rank} место {best_ranks.get(rank) if int(rank) <= 3 else ''}\n"
                        f"<em>Счёт</em>: {info.get('score').get('num_solved')}\n"
                        f"<em>Решённые задачи</em>: {len(solved_problems)}\n\n"
                        f"-------------------------------\n\n"
                        f"{message_problems}\n")

        await callback.message.edit_text(message_info, reply_markup=menu_ikb, parse_mode="HTML")
