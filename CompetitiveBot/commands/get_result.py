import logging
import time
from create import dp
from aiogram import types
from commands.submit_solution import solutionsID
from keyboards import after_result_ikb, return_result_ikb
from commands.url_requests import read_submission_source_code, read_problems, read_submissions, get_submission_verdict

judgement_types = {
    "AC": {"Name": "Accepted", "Description": "Solves the problem", "Description_rus": "🟩 Решение правильное!"},
    "RE": {"Name": "Rejected", "Description": "Does not solve the problem", "Description_rus": "🟥 Решение не верно"},
    "WA": {"Name": "Wrong Answer", "Description": "Output is not correct", "Description_rus": "🟥 Вывод неверен"},
    "TLE": {"Name": "Time Limit Exceeded", "Description": "🟨 Медленное выполнение программы"},
    "RTE": {"Name": "Run-Time Error", "Description": "🟥 Произошёл сбой"},
    "CE": {"Name": "Compile Error", "Description": "🟥 Решение не компилируется"},
    "APE": {"Name": "Accepted - Presentation Error",
            "Description": "Solves the problem, although formatting is wrong",
            "Description_rus": "Решает проблему, но форматирование неправильное"},
    "OLE": {"Name": "Output Limit Exceeded", "Description": "Output is larger than allowed"},
    "PE": {"Name": "Presentation Error", "Description": "Data in output is correct, but formatting is wrong"},
    "EO": {"Name": "Excessive Output", "Description": "A correct output is produced, but also additional output"},
    "IO": {"Name": "Incomplete Output	", "Description": "Parts, but not all, of a correct output is produced"},
    "NO": {"Name": "No Output", "Description": "There is no output"},
    "WTL": {"Name": "Wallclock Time Limit Exceeded",
            "Description": "CPU time limit is not exceeded, but wallclock is"},
    "ILE": {"Name": "Idleness Limit Exceeded", "Description": "No CPU time used for too long"},
    "TCO": {"Name": "Time Limit Exceeded - Correct Output",
            "Description": "Too slow but producing correct output"},
    "TWA": {"Name": "Time Limit Exceeded - Wrong Answer", "Description": "Too slow and also incorrect output"},
    "TPE": {"Name": "Time Limit Exceeded - Presentation Error",
            "Description": "Too slow and also presentation error"},
    "TEO": {"Name": "Time Limit Exceeded - Excessive Output",
            "Description": "Too slow and also excessive output"},
    "TIO": {"Name": "	Time Limit Exceeded - Incomplete Output",
            "Description": "Too slow and also incomplete output"},
    "TNO": {"Name": "Time Limit Exceeded - No Output", "Description": "Too slow and also no output"},
    "MLE": {"Name": "Memory Limit Exceeded", "Description": "Uses too much memory"},
    "SV": {"Name": "Security Violation",
           "Description": "Uses some functionality that is not allowed by the system"},
    "IF": {"Name": "Illegal Function	", "Description": "Calls a function that is not allowed by the system"},
    "RCO": {"Name": "Run-Time Error - Correct Output", "Description": "Crashing but producing correct output"},
    "RWA": {"Name": "Run-Time Error - Wrong Answer", "Description": "Crashing and also incorrect output"},
    "RPE": {"Name": "Run-Time Error - Presentation Error", "Description": "Crashing and also presentation error"},
    "REO": {"Name": "Run-Time Error - Excessive Output", "Description": "Crashing and also excessive output"},
    "RIO": {"Name": "Run-Time Error - Incomplete Output", "Description": "Crashing and also incomplete output"},
    "RNO": {"Name": "Run-Time Error - No Output", "Description": "Crashing and also no output"},
    "CTL": {"Name": "Compile Time Limit Exceeded	", "Description": "Compilation took too long"},
    "JE": {"Name": "Judging Error", "Description": "Something went wrong with the system"},
    "SE": {"Name": "Submission Error", "Description": "Something went wrong with the submission"},
    "CS": {"Name": "Contact Staff	", "Description": "Something went wrong"}
}


EXTENSIONS = {
    "cpp": "cpp",
    "c": "c",
    "python": "py",
    "java": "java",
    "python3": "py"
}


@dp.callback_query_handler(text='check_result')
async def show_tasks(callback: types.CallbackQuery):
    await callback.message.edit_text("Получаю данные...")
    timeout_seconds = 60
    start_time = time.time()
    submission = None

    while time.time() - start_time < timeout_seconds:
        try:
            submission = [s for s in read_submissions() if s["id"] == solutionsID[callback.from_user.id]][0]
            submission_verdict = get_submission_verdict(submission.get("id"))

            if submission_verdict:
                break
        except Exception as e:
            print(f"Error making API request: {e}")
            logging.exception(e)
            break
        time.sleep(1)
    print("submission", submission)

    if submission:
        # team_id = submission.get("team_id")
        problem_id = submission.get("problem_id")
        problem_name = "".join([p.get("name") for p in read_problems() if p.get("id") == problem_id])
        s_id = submission.get("id")
        language = submission.get("language_id")
        submission_verdict = get_submission_verdict(s_id)
        verdict_description = judgement_types.get(submission_verdict)

        text = (f"<b><em>Задача:</em></b> {problem_name}\n"
                f"<b><em>Язык программирования:</em></b> {language}\n")

        verdict_text = submission_verdict
        if verdict_description:
            verdict_values = list(verdict_description.values())
            verdict_text = f"{submission_verdict} - {verdict_values[0]}\n<em>{verdict_values[1]}</em>"
            if len(verdict_values) == 3:
                verdict_text += f"\n\n{verdict_values[2]}"

        text += "<b><em>Результат:</em></b>\n\n" + verdict_text

        await callback.message.edit_text(text, reply_markup=after_result_ikb, parse_mode='HTML')


@dp.callback_query_handler(text="code_source")
async def show_task_code(callback: types.CallbackQuery):
    submission = [s for s in read_submissions() if s["id"] == solutionsID[callback.from_user.id]][0]
    s_id = submission.get("id")

    if callback.data == "code_source":
        code_source = f"<code>{read_submission_source_code(s_id)}</code>"
        await callback.message.edit_text(code_source, reply_markup=return_result_ikb, parse_mode='HTML')