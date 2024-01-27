import requests
import json
import logging
import requests.utils
import base64
from config import admin_authorization, settings

PLATFORM_URL = "http://localhost:12345"
API_VERSION = "v4"
CONTEST_ID = "2"

# Шаблоны URL-адресов API
CONTESTS_URL_TEMPLATE = f'{PLATFORM_URL}/api/v4/contests'
CONTEST_SUBMISSIONS_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/contests/{CONTEST_ID}/submissions?strict=false"
CONTEST_PROBLEMS_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/contests/{CONTEST_ID}/problems?strict=false"
CONTEST_LANGUAGES_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/contests/{CONTEST_ID}/languages"
CONTEST_TEAMS_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/contests/{CONTEST_ID}/teams?public=true&strict=false"
SUBMISSION_JUDGEMENT_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/judgements?submission_id=SUBMISSION_ID&strict=false"
SUBMISSION_SOURCE_CODE_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/contests/{CONTEST_ID}/submissions/SUBMISSION_ID/source-code?strict=false"
CONTESTS_TEAMS_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/contests/{CONTEST_ID}/teams?strict=false"
CONTESTS_SCOREBOARD_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/contests/{CONTEST_ID}/scoreboard?strict=false"
USERS_URL_TEMPLATE = f"{PLATFORM_URL}/api/v4/users"
PROBLEM_URL_TEXT = f'{PLATFORM_URL}/api/v4/contests/{CONTEST_ID}/problems/PROBLEM_ID/statement?strict=false'


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


def read_scoreboard():
    """
    Функция для получения рейтинговой таблицы
    Returns: Данные рейтинговой таблицы
    """

    try:
        response = requests.get(CONTESTS_SCOREBOARD_URL_TEMPLATE)
        if response.status_code == 200:
            result = response.json()
            return result
        return None
    except RuntimeError as e:
        logging.warning(e)
        return None


def read_problem_text(p_id):
    """
    Функция для получения описания задачи
    Args: Идентификатор задачи
    Returns: Данные ответа
    """

    try:
        url = PROBLEM_URL_TEXT.replace('PROBLEM_ID', p_id)
        data = requests.get(url)
        return data if data else None
    except RuntimeError as e:
        logging.warning(e)
        return None


def read_teams():
    """
    Функция для получения всех команд
    Returns: данные ответа в формате JSON
    """

    try:
        url = CONTESTS_TEAMS_URL_TEMPLATE
        data = do_api_request(url)
        return data if data else None
    except RuntimeError as e:
        logging.warning(e)
        return None


def read_submissions():
    """
    Получает результаты соревнования.
    Returns: данные ответа в формате JSON
    """

    try:
        url = CONTEST_SUBMISSIONS_URL_TEMPLATE
        data = do_api_request(url)
        return data
    except RuntimeError as e:
        logging.warning(e)
        return None


def read_submission_source_code(submission_id):
    """
    Функция для получения исходного кода решения.
    Args:
        submission_id: Идентификатор решения
    Returns: Исходный код или None
    """

    try:
        url = SUBMISSION_SOURCE_CODE_URL_TEMPLATE.replace("SUBMISSION_ID", str(submission_id))
        data = do_api_request(url)
        if data:
            return decode(data[0]["source"])
        return None
    except RuntimeError as e:
        logging.warning(e)
        return None


def read_users():
    """
    Функция для получения всех пользователей
    Returns: Пользователи или None если возникла ошибка
    """
    try:
        data = do_api_request(USERS_URL_TEMPLATE)
    except RuntimeError as e:
        logging.warning(e)
        return None

    if not isinstance(data, list):
        logging.warning("DOMjudge's API returned unexpected JSON data for endpoint 'contests'.")
        return None

    users = []
    for user in data:
        if not user['id']:
            logging.warning("DOMjudge's API returned unexpected JSON data for 'contests'.")
            return None
        users.append(user)

    logging.info(f'Read {len(users)} contest(s) from the API.')
    return users


def read_contests():
    """
    Функция для получения всех соревнований
    Returns: Соревнования или None если возникла ошибка
    """

    try:
        data = do_api_request(CONTESTS_URL_TEMPLATE)
    except RuntimeError as e:
        logging.warning(e)
        return None

    if not isinstance(data, list):
        logging.warning("DOMjudge's API returned unexpected JSON data for endpoint 'contests'.")
        return None

    contests = []
    for contest in data:
        if ('id' not in contest
                or 'shortname' not in contest
                or not contest['id']
                or not contest['shortname']):
            logging.warning("DOMjudge's API returned unexpected JSON data for 'contests'.")
            return None
        contests.append(contest)

    logging.info(f'Read {len(contests)} contest(s) from the API.')
    return contests


def read_languages():
    """
    Функция для получения всех языков для текущего соревнования
    Returns: Языки или None если возникла ошибка
    """

    try:
        data = do_api_request(CONTEST_LANGUAGES_URL_TEMPLATE)
    except RuntimeError as e:
        logging.warning(e)
        return None

    if not isinstance(data, list):
        logging.warning("DOMjudge's API returned unexpected JSON data for endpoint 'languages'.")
        return None

    languages = []

    for item in data:
        if ('id' not in item
                or 'extensions' not in item
                or not item['id']
                or not isinstance(item['extensions'], list)
                or len(item['extensions']) == 0):
            logging.warning("DOMjudge's API returned unexpected JSON data for 'languages'.")
            return None
        language = {
            'id': item['id'],
            'name': item['name'],
            'entry_point_required': item['entry_point_required'] or False,
            'extensions': {item['id']}
        }
        language['extensions'] |= set([ext for ext in item['extensions']])
        languages.append(language)

    logging.info(f'Read {len(languages)} language(s) from the API.')

    return languages


def read_problems():
    """
    Функция для получения всех задач текущего соревнования
    Returns: Задачи или None если возникла ошибка
    """

    try:
        data = do_api_request(CONTEST_PROBLEMS_URL_TEMPLATE)
    except RuntimeError as e:
        logging.warning(e)
        return None

    if not isinstance(data, list):
        logging.warning("DOMjudge's API returned unexpected JSON data for endpoint 'problems'.")
        return None

    problems = []

    for problem in data:
        if ('id' not in problem
                or 'label' not in problem
                or not problem['id']
                or not problem['label']):
            logging.warning("DOMjudge's API returned unexpected JSON data for 'problems'.")
            return None
        problems.append(problem)

    logging.info(f'Read {len(problems)} problem(s) from the API.')

    return problems


def get_submission_judgement(submission_id):
    """
        Функция для получения информации о судействе решения
    Args:
        submission_id: Идентификатор решения
    Returns: Данные об оценке в формате json
    """

    try:
        url = SUBMISSION_JUDGEMENT_URL_TEMPLATE.replace("SUBMISSION_ID", str(submission_id))
        data = do_api_request(url)
        return data if data else None
    except RuntimeError as e:
        logging.warning(e)
        return None


def get_submission_verdict(submission_id):
    """
    Получение вердикта для решения задачи
    Args:
        submission_id: Идентификатор решения
    Returns: Аббревиатура результата или None
    """

    try:
        for judgement in get_submission_judgement(submission_id):
            print(judgement)
            if judgement["valid"] is True:
                return judgement["judgement_type_id"]
        return None
    except RuntimeError as e:
        logging.warning(e)
        return None


def do_api_request(url: str):
    """
    Выполняет вызов API для данного запроса и возвращает его данные
    Args:
        url:

    Returns: Содержимое запроса
    """
    session = admin_authorization(settings.admin_username, settings.admin_password)

    if not PLATFORM_URL:
        raise RuntimeError('No baseurl set')

    logging.info(f'Connecting to {url}')

    try:
        response = session.get(url)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(e)

    if response.status_code >= 300:
        print(response.text)
        if response.status_code == 401:
            raise RuntimeError('Authentication failed, please check your DOMjudge credentials in ~/.netrc.')
        else:
            raise RuntimeError(f'API request {url} failed (code {response.status_code}).')

    logging.debug(f"API call '{url}' returned:\n{response.text}")

    return json.loads(response.text)


def do_api_submit(problem_id, lang_id, headers, filenames):
    """
    Отправляет решение задачи
    Args:
        problem_id: Идентификатор задачи
        lang_id: Идентификатор языка программирования
        headers: Заголовки HTTP-запроса
        filenames: Файлы с решением

    Returns: True/False - результат отправки запроса, идентификатор отправленного решения
    """

    data = {
        'problem': f'{problem_id}',
        'language': f'{lang_id}',
    }
    # if entry_point:
    #    data['entry_point'] = entry_point

    files = [('code[]', open(filename, 'rb')) for filename in filenames]

    logging.info(f'connecting to {CONTEST_SUBMISSIONS_URL_TEMPLATE}')

    response = requests.post(CONTEST_SUBMISSIONS_URL_TEMPLATE, data=data, files=files, headers=headers)

    logging.debug(f"API call 'submissions' returned:\n{response.text}")

    # Соединение сработало, но, возможно, мы получили сообщение об ошибке HTTP
    if response.status_code >= 300:
        if response.status_code == 401:
            raise RuntimeError('Authentication failed, please check your DOMjudge credentials in ~/.netrc.')
        else:
            raise RuntimeError(f'Submission failed (code {response.status_code})')

    # Мы получили успешный HTTP-ответ.
    # Но проверим, действительно ли мы получили идентификатор отправки.
    try:
        submission = json.loads(response.text)
    except json.decoder.JSONDecodeError as e:
        error_text = f"Parsing DOMjudge\'s API output failed: {e}"
        logging.error(error_text)
        err = f"Ошибка: {error_text}"
        return False, err

    if not isinstance(submission, dict) or not 'id' in submission or not isinstance(submission['id'], str):
        error_text = "DOMjudge\'s API returned unexpected JSON data."
        logging.error(error_text)
        err = f"Ошибка: {error_text}"
        return False, err

    return True, submission['id']
