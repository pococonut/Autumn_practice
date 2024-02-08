import logging
import time
from aiogram import types, F
from create import dp
from keyboards import after_result_ikb
from commands.menu import global_Dict_del_msg
from commands.result_types import judgement_types
from commands.general_func import write_user_values
from commands.submit_solution import globalDict_solutions
from commands.url_requests import read_problems, read_submissions, get_submission_verdict


def get_submission(usr_id):
    """
    Функция для получения отправленного пользователем решения из всего списка решений
    Args:
        usr_id: Идентификатор пользователя

    Returns: Решение
    """

    for submission in read_submissions():
        if submission["id"] == globalDict_solutions[usr_id]:
            return submission
    return None


def check_submission_verdict(submission):
    """
    Функция для ожидания результата сервера судьи
    Args:
        submission: Решение задачи

    Returns: Вердикт о решении задачи
    """

    start_time = time.time()
    while time.time() - start_time < 60:
        try:
            submission_verdict = get_submission_verdict(submission.get("id"))
            if submission_verdict:
                return submission_verdict
        except Exception as e:
            logging.exception(e)
            return None
        time.sleep(1)
    return None


def get_verdict_text(submission_abbreviation):
    """
    Функция для получения ответа на решение
    Args:
        submission_abbreviation: Аббревиатура результата судейства

    Returns: Ответ на решение
    """

    if not submission_abbreviation:
        return "Произошел сбой, повторите отправку позже."

    verdict_data = judgement_types.get(submission_abbreviation)

    if verdict_data:
        verdict_values = list(verdict_data.values())
        name = verdict_values[0]
        en_description = verdict_values[1]
        ru_description = verdict_values[2]

        return f"{submission_abbreviation} - {name}\n<em>{en_description}</em>\n\n{ru_description}"

    return submission_abbreviation


def get_problem_name(submission):
    """
    Функция для получения названия задачи, на которую было отправлено решение
    Args:
        submission: Решение задачи

    Returns: Названия задачи
    """

    for problem in read_problems():
        if problem.get("id") == submission.get("problem_id"):
            return problem.get("name")
    return None


@dp.callback_query(F.data == 'check_result')
async def show_user_result(callback: types.CallbackQuery):
    """
    Функция для получения результата тестирования решения задачи
    """

    await callback.message.edit_text("Получаю данные...")
    usr_id = str(callback.from_user.id)
    submission = get_submission(usr_id)

    if not submission:
        judge_response = "Произошел сбой, повторите отправку позже."
    else:
        submission_abbreviation = check_submission_verdict(submission)
        verdict_text = get_verdict_text(submission_abbreviation)
        problem_name = get_problem_name(submission)
        submission_lang = submission.get('language_id')

        judge_response = (f"<b><em>Задача:</em></b> {problem_name}\n"
                          f"<b><em>Язык программирования:</em></b> {submission_lang}\n"
                          f"<b><em>Результат:</em></b>\n\n {verdict_text}")

    sent_msg = await callback.message.edit_text(judge_response, reply_markup=after_result_ikb)
    global_Dict_del_msg[usr_id] = sent_msg.message_id
    write_user_values("global_Dict_del_msg", global_Dict_del_msg)
