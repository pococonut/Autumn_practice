import logging
import time
from commands.menu import global_Dict_del_msg
from commands.result_types import judgement_types
from create import dp
from aiogram import types, F
from commands.submit_solution import globalDict_solutions
from keyboards import after_result_ikb
from commands.url_requests import read_problems, read_submissions, get_submission_verdict


@dp.callback_query(F.data == 'check_result')
async def show_tasks(callback: types.CallbackQuery):
    """
    Функция для получения результата тестирования решения задачи
    """

    await callback.message.edit_text("Получаю данные...")
    submission = [s for s in read_submissions() if s["id"] == globalDict_solutions[callback.from_user.id]][0]

    if not submission:
        text = "Произошел сбой, повторите отправку позже."
    else:
        submission_verdict = None
        start_time = time.time()
        while time.time() - start_time < 60:
            try:
                submission_verdict = get_submission_verdict(submission.get("id"))
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

        problem_name = "".join([p.get("name") for p in read_problems() if p.get("id") == submission.get("problem_id")])
        text = (f"<b><em>Задача:</em></b> {problem_name}\n"
                f"<b><em>Язык программирования:</em></b> {submission.get('language_id')}\n"
                f"<b><em>Результат:</em></b>\n\n {verdict_txt}")

    sent_msg = await callback.message.edit_text(text, reply_markup=after_result_ikb)
    global_Dict_del_msg[callback.from_user.id] = sent_msg.message_id
