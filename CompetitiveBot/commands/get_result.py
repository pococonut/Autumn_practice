import logging
import time
from commands.result_types import judgement_types
from create import dp
from aiogram import types
from commands.submit_solution import globalDict_solutions
from keyboards import after_result_ikb, return_result_ikb
from commands.url_requests import read_submission_source_code, read_problems, read_submissions, get_submission_verdict


@dp.callback_query_handler(text='check_result')
async def show_tasks(callback: types.CallbackQuery):
    """
    Функция для получения результата тестирования решения задачи
    """

    await callback.message.edit_text("Получаю данные...")
    submission = [s for s in read_submissions() if s["id"] == globalDict_solutions[callback.from_user.id]][0]

    if not submission:
        text = "Произошел сбой, повторите отправку позже."
    else:
        problem_id = submission.get("problem_id")
        s_id = submission.get("id")
        problem_name = "".join([p.get("name") for p in read_problems() if p.get("id") == problem_id])
        language = submission.get("language_id")

        submission_verdict = None
        start_time = time.time()
        while time.time() - start_time < 60:
            try:
                submission_verdict = get_submission_verdict(s_id)
                if submission_verdict:
                    break
            except Exception as e:
                logging.exception(e)
                break
            time.sleep(1)

        if not submission_verdict:
            verdict_txt = "Произошел сбой, повторите отправку позже."
        else:
            verdict_description = judgement_types.get(submission_verdict)
            verdict_txt = submission_verdict
            if verdict_description:
                verdict_val = list(verdict_description.values())
                verdict_txt = f"{submission_verdict} - {verdict_val[0]}\n<em>{verdict_val[1]}</em>\n\n{verdict_val[2]}"

        text = (f"<b><em>Задача:</em></b> {problem_name}\n"
                f"<b><em>Язык программирования:</em></b> {language}\n"
                f"<b><em>Результат:</em></b>\n\n {verdict_txt}")

    await callback.message.edit_text(text, reply_markup=after_result_ikb, parse_mode='HTML')


@dp.callback_query_handler(text="code_source")
async def show_task_code(callback: types.CallbackQuery):
    """
    Функция вывода исходного кода решения
    """

    submission = [s for s in read_submissions() if s["id"] == globalDict_solutions[callback.from_user.id]][0]
    code_source = f"<code>{read_submission_source_code(submission.get('id'))}</code>"
    await callback.message.edit_text(code_source, reply_markup=return_result_ikb, parse_mode='HTML')