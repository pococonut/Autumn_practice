import time
import requests
import base64
from create import dp
from aiogram import types
from config import settings
from commands.submit_solution import solutionsID
from keyboards import menu_keyboard

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

# Аутентификация
USERNAME = settings.admin_username
PASSWORD = settings.admin_password

# Создаем объект сеанса
session = requests.Session()
# Выполняем проверку подлинности
session.auth = (USERNAME, PASSWORD)

PLATFORM_URL = "http://localhost:12345"

# Шаблоны URL-адресов API
CONTEST_SUBMISSIONS_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/contests/CONTEST_ID/submissions?strict=false"
CONTEST_PROBLEMS_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/contests/CONTEST_ID/problems?strict=false"
CONTEST_TEAMS_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/contests/CONTEST_ID/teams?public=true&strict=false"
SUBMISSION_JUDGEMENT_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/judgements?submission_id=SUBMISSION_ID&strict=false"
SUBMISSION_SOURCE_CODE_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/contests/CONTEST_ID/submissions/SUBMISSION_ID/source-code?strict=false"

EXTENSIONS = {
    "cpp": "cpp",
    "c": "c",
    "python": "py",
    "java": "java",
    "python3": "py"
}


def decode(base64_string):
    """
    Декодирует строку, закодированную в utf-8.
    Args:
        base64_string: Исходный код решения
    Returns: Возвращает декодированную строку
    """
    try:
        decoded_bytes = base64.b64decode(base64_string)
        decoded_string = decoded_bytes.decode('utf-8')
        return decoded_string
    except Exception as e:
        print("Error decoding Base64 string:", str(e))


def get_json_response(request_url):
    """
    Отправляет GET запрос по указанному URL-адресу и возвращает данные ответа в формате JSON.
    Args:
        request_url: url адрес
    Returns: Данные ответа в формате JSON
    """

    response = session.get(request_url)

    data = None

    # Check the response status code
    if response.status_code == 200:
        # Request was successful
        data = response.json()  # Get the response data in JSON format
    else:
        # Request failed
        print("Request failed with status code:", response.status_code)

    return data


def get_contest_problems(contest_id):
    """
    Get the problems for a contest.
    """
    url = CONTEST_PROBLEMS_URL_TEMPLATE.replace("CONTEST_ID", str(contest_id))

    return get_json_response(url)


def get_contest_submissions(contest_id):
    """
    Получает результаты соревнования.
    Args:
        contest_id: Идентификатор соревнования
    Returns: данные ответа в формате JSON
    """
    url = CONTEST_SUBMISSIONS_URL_TEMPLATE.replace("CONTEST_ID", str(contest_id))

    return get_json_response(url)


def get_submission_source_code(contest_id, submission_id):
    """
    Функция для получения исходного кода решения.
    Args:
        contest_id: Идентификатор соревнования
        submission_id: Идентификатор решения
    Returns: Исходный код или None

    """
    url = SUBMISSION_SOURCE_CODE_URL_TEMPLATE.replace("CONTEST_ID", str(contest_id)) \
        .replace("SUBMISSION_ID", str(submission_id))

    data = get_json_response(url)

    if data is not None:
        return decode(data[0]["source"])
    else:
        return None


def get_submission_judgement(submission_id):
    """
        Функция для получения информации о судействе решения
    Args:
        submission_id: Идентификатор решения
    Returns: Данные об оценке в формате json
    """
    url = SUBMISSION_JUDGEMENT_URL_TEMPLATE.replace("SUBMISSION_ID", str(submission_id))

    return get_json_response(url)


def get_submission_verdict(submission_id):
    """
    Получение вердикта для решения
    Args:
        submission_id: Идентификатор решения
    Returns:
    """
    for judgement in get_submission_judgement(submission_id):
        print(judgement)
        if judgement["valid"] is True:
            return judgement["judgement_type_id"]

    return None


@dp.callback_query_handler(text='check_result')
async def show_tasks(callback: types.CallbackQuery):
    await callback.message.edit_text("Получаю данные...")
    time.sleep(5)
    contest_id = 2
    submission = [s for s in get_contest_submissions(contest_id) if s["id"] == solutionsID[callback.from_user.id]][0]

    #team_id = submission.get("team_id")

    problem_id = submission.get("problem_id")
    problem_name = "".join([p.get("name") for p in get_contest_problems('2') if p.get("id") == problem_id])
    s_id = submission.get("id")
    language = submission.get("language_id")
    code_source = get_submission_source_code(contest_id, s_id)

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

    # f"{[judgement_types[submission_verdict].values()]}\n"

    await callback.message.edit_text(text, reply_markup=menu_keyboard, parse_mode='HTML')

