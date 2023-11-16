import time
import requests
import base64
from create import dp
from aiogram import types
from config import settings
from commands.submit_solution import solutionsID
from keyboards import menu_keyboard


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

contest_id = 2
problem_id = '7'
for s in get_contest_submissions(contest_id):
    print(s["id"], problem_id)
