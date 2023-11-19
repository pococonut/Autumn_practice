import requests
import argparse
import datetime
import json
import logging
import os
import requests.utils
import stat
import sys
import time
import base64
from commands.get_tasks import problemIdDict
from create import dp, bot
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from config import settings
from keyboards import languages_ikb, back_ikb, check_result_ikb

try:
    import magic
except ModuleNotFoundError:
    # Ignore, magic is optional
    magic = None

solutionsID = {}


class File(StatesGroup):
    lang = State()
    file = State()

def read_contests(baseurl, api_version, headers) -> list:
    """Read all contests from the API.

    Returns:
        The contests or None if an error occurred.
    """

    try:
        data = do_api_request(baseurl, api_version, headers, 'contests')
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


def read_languages(baseurl, api_version, headers, contest_id) -> list:
    """Read all languages for the current contest from the API.

    Returns:
        The languages or None if an error occurred.
    """

    try:
        endpoint = 'contests/' + contest_id + '/languages'
        data = do_api_request(baseurl, api_version, headers, endpoint)
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


def read_problems(baseurl, api_version, headers, contest_id) -> list:
    '''Read all problems for the current contest from the API.

    Returns:
        The problems or None if an error occurred.
    '''

    try:
        endpoint = 'contests/' + contest_id + '/problems'
        data = do_api_request(baseurl, api_version, headers, endpoint)
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


def do_api_request(baseurl, api_version, headers, name: str):
    """Perform an API call to the given endpoint and return its data.

    Parameters:
        name (str): the endpoint to call

    Returns:
        The endpoint contents.

    Raises:
        RuntimeError when the response is not JSON or the HTTP status code is non 2xx.
    """

    if not baseurl:
        raise RuntimeError('No baseurl set')

    url = f'{baseurl}api/{api_version}/{name}'

    logging.info(f'Connecting to {url}')

    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(e)

    if response.status_code >= 300:
        print(response.text)
        if response.status_code == 401:
            raise RuntimeError('Authentication failed, please check your DOMjudge credentials in ~/.netrc.')
        else:
            raise RuntimeError(f'API request {name} failed (code {response.status_code}).')

    logging.debug(f"API call '{name}' returned:\n{response.text}")

    return json.loads(response.text)


def do_api_submit(problem_id, lang_id, contest_id, api_version, baseurl, headers, filenames):
    """Submit to the API with the given data."""

    data = {
        'problem': f'{problem_id}',
        'language': f'{lang_id}',
    }
    #if entry_point:
    #    data['entry_point'] = entry_point

    files = [('code[]', open(filename, 'rb')) for filename in filenames]

    url = f"{baseurl}api/{api_version}/contests/{contest_id}/submissions"
    logging.info(f'connecting to {url}')

    response = requests.post(url, data=data, files=files, headers=headers)

    logging.debug(f"API call 'submissions' returned:\n{response.text}")

    # The connection worked, but we may have received an HTTP error
    if response.status_code >= 300:
        print(response.text)
        if response.status_code == 401:
            raise RuntimeError('Authentication failed, please check your DOMjudge credentials in ~/.netrc.')
        else:
            raise RuntimeError(f'Submission failed (code {response.status_code})')

    # We got a successful HTTP response. It worked.
    # But check that we indeed received a submission ID.

    try:
        submission = json.loads(response.text)
    except json.decoder.JSONDecodeError as e:
        err = "Ошибка: Parsing DOMjudge\'s API output failed: {e}"
        return False, err

    if (not isinstance(submission, dict)
        or not 'id' in submission
        or not isinstance(submission['id'], str)):
        err = "Ошибка: DOMjudge\'s API returned unexpected JSON data."
        return False, err

    time = datetime.datetime.fromisoformat(submission['time']).strftime('%H:%M:%S')
    sid = submission['id']
    print(f"Submission received: id = s{sid}, time = {time}")
    print(f"Check {baseurl}team/submission/{sid} for the result.")

    return True, sid


async def download_file(filename, file_id):
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    file_url = f"https://api.telegram.org/file/bot{settings.api}/{file_path}"
    # Скачиваем файл
    response = requests.get(file_url)
    # Сохраняем файл на локальном компьютере

    """if os.path.exists(filename):
        os.rename(f'{filename}', f'{old_filename}.txt')"""

    with open(filename, 'wb') as f:
        f.write(response.content)


@dp.callback_query_handler(text=['solution'])
async def wait_file(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите язык.", reply_markup=languages_ikb)

    await File.lang.set()

previous_messages = {}


@dp.callback_query_handler(state=File.lang)
async def get_lang_file(callback: types.CallbackQuery, state: FSMContext):
    languages_id = {"lang_C": ["c", "c"],
                    "lang_C++": ["cpp", "cpp"],
                    "lang_Java": ["java", "java"],
                    "lang_Python": ["python3", "py"]}
    await state.update_data(lang=languages_id[callback.data])
    await callback.message.edit_text("Отправьте файл с решением.", reply_markup=back_ikb)
    previous_messages[str(callback.from_user.id)] = callback.message.message_id
    await File.next()


@dp.message_handler(content_types=types.ContentTypes.DOCUMENT, state=File.file)
async def handle_document(message: types.Message, state: FSMContext):
    # Получаем информацию о файле
    file_id = message.document.file_id
    # Скачиваем и сохраняем файл
    contest_id = '2'
    problem_id = problemIdDict[f'{message.from_user.id}']
    print('!!!!!!!!', problem_id)

    url_get_users = "http://localhost:12345/api/v4/users"

    username = settings.admin_username
    password = settings.admin_password
    session = requests.Session()
    session.auth = (username, password)

    response_get_users = session.get(url_get_users)
    for u in response_get_users.json():
        if str(message.from_user.id) == u.get("username").split("_")[-1]:
            print(u)
            username = u.get("username")
            break

    data = await state.get_data()
    await state.finish()
    filename = f'files/solutions/solution_{contest_id}_{problem_id}_{message.from_user.id}.{data["lang"][1]}'

    await download_file(filename, file_id)
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=previous_messages[str(message.from_user.id)])

    language_id = data["lang"][0]
    password = f"user_{str(message.from_user.id)}"
    # password = '1234567890'
    baseurl = 'http://localhost:12345/'
    api_version = 'v4'
    filenames = [f'{filename}']

    headers = {'user-agent': f'domjudge-submit-client ({requests.utils.default_user_agent()})'}
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers['Authorization'] = f'Basic {credentials}'

    submit_connection, data = do_api_submit(problem_id, language_id, contest_id, api_version, baseurl, headers, filenames)

    if submit_connection:
        await message.answer('Решение было получено.', reply_markup=check_result_ikb)
        solutionsID[message.from_user.id] = data
    else:
        await message.answer(f'Ошибка при отправке решения: {data}.')


