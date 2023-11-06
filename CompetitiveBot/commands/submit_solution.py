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
from keyboards import languages_ikb, back_ikb

try:
    import magic
except ModuleNotFoundError:
    # Ignore, magic is optional
    magic = None

"""contest_id = '2'
problem_id = '1'
lang_id = 'python3'

username = 'demo'
password = '1234567890'
baseurl = 'http://localhost:12345/'
api_version = 'v4'

headers = {'user-agent': f'domjudge-submit-client ({requests.utils.default_user_agent()})'}
credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
headers['Authorization'] = f'Basic {credentials}'

warn_mtime_minutes = 5
num_warnings = 0"""


def confirm(message: str) -> bool:
    answer = ''
    while answer not in ['y', 'n']:
        answer = input(f'{message} (y/n) ').lower()
    return answer == 'y'


def usage(msg: str):
    logging.error(f'error: {msg}')
    print(f"Type '{sys.argv[0]} --help' to get help.")
    exit(1)


def error(msg: str):
    logging.error(msg)
    exit(-1)


def warn_user(args, msg: str):
    global num_warnings
    num_warnings += 1
    if args.quiet:
        logging.debug(f'user warning #{num_warnings}: {msg}')
    else:
        print(f'WARNING: {msg}!')


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
        error(f'Parsing DOMjudge\'s API output failed: {e}')
        err = "Ошибка: Parsing DOMjudge\'s API output failed: {e}"
        return False

    if (not isinstance(submission, dict)
        or not 'id' in submission
        or not isinstance(submission['id'], str)):
        error('DOMjudge\'s API returned unexpected JSON data.')
        err = "Ошибка: DOMjudge\'s API returned unexpected JSON data."
        return False

    time = datetime.datetime.fromisoformat(submission['time']).strftime('%H:%M:%S')
    sid = submission['id']
    return True

    # print(f"Submission received: id = s{sid}, time = {time}")
    # print(f"Check {baseurl}team/submission/{sid} for the result.")


def kotlin_base_entry_point(filebase: str) -> str:
    if filebase == "":
        return "_"
    chars = list(filebase)
    for idx, c in enumerate(chars):
        if not c.isalnum():
            chars[idx] = "_"

    if chars[0].isalnum():
        chars[0] = chars[0].upper()
        filebase = "".join(chars)
    else:
        filebase = "_" + "".join(chars)

    return filebase


def get_epilog(contests, problems, languages, baseurl):
    '''Get the epilog for the help text.'''

    contests_part_one = None
    contests_part_two = None

    if not contests or len(contests) <= 1:
        contests_part_one = '''For CONTEST use the ID or short name as shown in the top-right contest
         drop-down box in the web interface.'''
        if contests and len(contests) == 1:
            contests_part_two = f"Currently this defaults to the only active contest '{contests[0]['shortname']}'"
    else:
        contests_part_one = 'For CONTEST use one of the following:'
        max_length = max([len(c['shortname']) for c in contests])
        for contest in contests:
            contests_part_one += f"\n    {contest['shortname']:<{max_length}} - {contest['name']}"

    if not problems:
        problem_part = 'For PROBLEM use the label as on the scoreboard.'
    else:
        problem_part = 'For PROBLEM use one of the following:'
        max_length = max([len(p['label']) for p in problems])
        for problem in problems:
            problem_part += f"\n    {problem['label']:<{max_length}} - {problem['name']}"

    if not languages:
        language_part = 'For LANGUAGE use the ID or a common extension.'
    else:
        language_part = 'For LANGUAGE use one of the following IDs or extensions:'
        max_length = max([len(l['name']) for l in languages])
        for language in languages:
            sorted_exts = ', '.join(sorted(language['extensions']))
            language_part += f"\n    {language['name']:<{max_length}} - {sorted_exts}"

    submit_client = sys.argv[0]
    epilog_parts = [
        "Explanation of submission options:",
        contests_part_one,
        contests_part_two,
        problem_part,
        '''When not specified, PROBLEM defaults to the first FILENAME excluding the
extension. For example, 'B.java' indicates the problem 'B'.''',
        language_part,
        '''The default for LANGUAGE is the extension of FILENAME. For example,
'B.java' indicates a Java submission.''',
        "Set URL to the base address of the webinterface without the 'team/' suffix.\n" +
        (f"The (pre)configured URL is '{baseurl}'\n" if baseurl else '') +
        "Credentials are read from ~/.netrc (see netrc(4) for details).",
        f'''Examples:

Submit problem 'b' in Java:
    {submit_client} b.java

Submit problem 'z' in C# for contest 'demo':
    {submit_client} --contest=demo z.cs

Submit problem 'e' in C++:
    {submit_client} --problem e --language=cpp ProblemE.cc

Submit problem 'hello' in C (options override the defaults from FILENAME):
    {submit_client} -p hello -l C HelloWorld.cpp

Submit multiple files (the problem and language are taken from the first):
    {submit_client} hello.java message.java''',
    ]

    return "\n\n".join(part for part in epilog_parts if part)


class File(StatesGroup):
    lang = State()
    file = State()


@dp.callback_query_handler(text=['solution'])
async def wait_file(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите язык.", reply_markup=languages_ikb)

    await File.lang.set()


@dp.callback_query_handler(state=File.lang)
async def get_lang_file(callback: types.CallbackQuery, state: FSMContext):
    languages_id = {"lang_C": "c",
                    "lang_C++": "cpp",
                    "lang_Java": "java",
                    "lang_Python": "python3"}
    await state.update_data(lang=languages_id[callback.data])
    await callback.message.edit_text("Отправьте файл с решением.", reply_markup=back_ikb)
    await File.next()


async def download_file(file_id):
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    file_url = f"https://api.telegram.org/file/bot{settings.api}/{file_path}"

    # Скачиваем файл
    response = requests.get(file_url)

    # Сохраняем файл на локальном компьютере
    with open('files/solutions/test.py', 'wb') as f:
        f.write(response.content)


@dp.message_handler(content_types=types.ContentTypes.DOCUMENT, state=File.file)
async def handle_document(message: types.Message, state: FSMContext):
    # Получаем информацию о файле
    file_id = message.document.file_id
    # Скачиваем и сохраняем файл
    await download_file(file_id)
    data = await state.get_data()
    await state.finish()

    contest_id = '2'
    problem_id = problemIdDict[f'{message.from_user.id}']
    language_id = data["lang"]
    username = 'demo'
    password = '1234567890'
    baseurl = 'http://localhost:12345/'
    api_version = 'v4'

    headers = {'user-agent': f'domjudge-submit-client ({requests.utils.default_user_agent()})'}
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers['Authorization'] = f'Basic {credentials}'

    warn_mtime_minutes = 5
    num_warnings = 0

    version_text = '''
    submit -- part of DOMjudge
    Written by the DOMjudge developers

    DOMjudge comes with ABSOLUTELY NO WARRANTY.  This is free software, and you
    are welcome to redistribute it under certain conditions.  See the GNU
    General Public Licence for details.
    '''

    loglevels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }

    # Note: we set add_help to false since we can only print the help text after
    # parsing flags, since the help contains data needed from the API.
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Submit a solution for a problem.',
        add_help=False)
    parser.add_argument('--version', action='version', version=version_text, help='output version information and exit')
    parser.add_argument('-h', '--help', help='display this help and exit', action='store_true')
    parser.add_argument('-c', '--contest', help='''submit for contest with ID or short name CONTEST.
        Defaults to the value of the
        environment variable 'SUBMITCONTEST'.
        Mandatory when more than one contest is active.''')
    parser.add_argument('-p', '--problem', help='submit for problem with ID or label PROBLEM', default='')
    parser.add_argument('-l', '--language', help='submit in language with ID LANGUAGE', default='')
    parser.add_argument('-e', '--entry_point', help='set an explicit entry_point, e.g. the java main class')
    parser.add_argument('-v', '--verbose', help='increase verbosity', choices=loglevels.keys(), nargs='?', const='INFO',
                        default='WARNING')
    parser.add_argument('-q', '--quiet', help='suppress warning/info messages', action='store_true')
    parser.add_argument('-y', '--assume-yes', help='suppress user input and assume yes', action='store_true')
    parser.add_argument('-u', '--url', help='''submit to server with base address URL
        (should not be necessary for normal use)''')
    parser.add_argument('filename', nargs='*', help='filename(s) to submit')

    args = parser.parse_args()

    verbosity = args.verbose
    if args.quiet:
        verbosity = 'ERROR'

    logging.basicConfig(format=f'%(message)s', level=loglevels[verbosity])
    logging.info(f'set verbosity to {verbosity}')

    # problem_id = args.problem
    # language_id = args.language
    entry_point = args.entry_point

    if args.url:
        baseurl = args.url
    elif 'SUBMITBASEURL' in os.environ:
        baseurl = os.environ['SUBMITBASEURL']
    # Make sure that baseurl terminates with a '/' for later concatenation.
    if baseurl and baseurl[-1:] != '/':
        baseurl += '/'

    contests = read_contests(baseurl, api_version, headers) if baseurl else None
    if not contests and not args.help:
        logging.warning('Could not obtain active contests.')

    my_contest = None
    my_language = None
    my_problem = None

    for c in contests:
        if contest_id == c.get('id'):
            my_contest = c
            break

    if not contest_id:
        if not contests:
            if not args.help:
                warn_user(args, 'No active contests found (and no contest specified)')
        elif len(contests) == 1:
            my_contest = contests[0]
        else:
            shortnames = ', '.join([c['shortname'] for c in contests])
            warn_user(args, f"Multiple active contests found, please specify one of {shortnames}")
            print(contests)

    elif contests:
        contest_id = contest_id.lower()
        for contest in contests:
            if contest['id'].lower() == contest_id or contest['shortname'].lower() == contest_id:
                my_contest = contest
                break

    languages = None
    problems = None
    if my_contest and baseurl:
        if 'allow_submit' in my_contest and not my_contest['allow_submit']:
            warn_user(args, 'Submissions for contest (temporarily) disabled')
            exit(1)
        languages = read_languages(baseurl, api_version, headers, contest_id)
        problems = read_problems(baseurl, api_version, headers, contest_id)

    parser.epilog = get_epilog(contests, problems, languages, baseurl)

    if args.help:
        if 'BATS_VERSION' in os.environ:
            # print_help adds line breaks depending on the number of available columns.
            # To make it deterministic under test, we set it to 100 here if we are testing.
            os.environ['COLUMNS'] = '100'
        parser.print_help()
        exit(0)

    if not baseurl:
        usage('No contest url specified, pass it as --url or set as SUBMITBASEURL environment variable.')

    if not my_contest:
        usage('No (valid) contest specified, pass it as --contest or set as SUBMITCONTEST environment variable.')

    if not languages:
        logging.warning('Could not obtain language data.')

    if not problems:
        logging.warning('Could not obtain problem data.')

    # Process all source files
    filenames = ['files/solutions/test.py']
    for index, filename in enumerate(args.filename, 1):
        # Ignore doubly specified files
        if filename in filenames:
            logging.debug(f"Ignoring doubly specified file `{filename}'.")
            continue

        # Stat file and do some validation checks
        try:
            st = os.stat(filename)
        except FileNotFoundError:
            usage(f"Cannot find file `{filename}'.")

        logging.debug(f"submission file {index}: `{filename}'")

        # Do some checks on submission file and warn user
        if not stat.S_ISREG(st.st_mode):
            warn_user(args, f"`{filename}' is not a regular file")
        if not st.st_mode & stat.S_IRUSR:
            warn_user(args, f"`{filename}' is not readable")
        if st.st_size == 0:
            warn_user(args, f"`{filename}' is empty")

        file_age = (time.time() - st.st_mtime) / 60
        if file_age > warn_mtime_minutes:
            warn_user(args, f"`{filename}' has not been modified for {int(file_age)} minutes")

        if magic:
            m = magic.from_file(filename, mime=True)
            if m[:5] != 'text/':
                warn_user(args, f"`{filename}' is detected as binary/data")

        filenames.append(filename)

    # Try to parse problem and language from first filename.

    filebase = os.path.basename(filenames[0])

    if '.' in filebase:
        dot = filebase.rfind('.')
        ext = filebase[dot + 1:]
        filebase = filebase[:dot]

        if not problem_id:
            problem_id = filebase
        if not language_id:
            language_id = ext

    # Check for languages matching file extension.
    language_id = language_id.lower()
    for language in languages:
        for extension in language['extensions']:
            if extension.lower() == language_id:
                my_language = language
                break
        if my_language:
            break

    if not my_language:
        usage('No known language specified or detected.')

    # Check for problem matching ID or label.
    problem_id = '4'
    for problem in problems:
        print(problem['id'].lower(), problem_id)
        if problem['id'].lower() == problem_id or problem['label'].lower() == problem_id:
            my_problem = problem
            break

    if not my_problem:
        usage('No known problem specified or detected.')

    # Guess entry point if not already specified.
    if not entry_point and my_language['entry_point_required']:
        if my_language['name'] == 'Java':
            entry_point = filebase
        elif my_language['name'] == 'Kotlin':
            entry_point = kotlin_base_entry_point(filebase) + "Kt"
        elif my_language['name'] == 'Python 3':
            entry_point = filebase + "." + ext

    if not entry_point and my_language['entry_point_required']:
        error('Entry point required but not specified nor detected.')

    logging.debug(f"contest is `{my_contest['shortname']}'")
    logging.debug(f"problem is `{my_problem['label']}'")
    logging.debug(f"language is `{my_language['name']}'")
    logging.debug(f"entry_point is `{entry_point or '<None>'}'")
    logging.debug(f"url is `{baseurl}'")

    if not args.assume_yes:
        print('Submission information:')
        print(filenames)
        if len(filenames) == 1:
            print(f'  filename:    {filenames[0]}')
        else:
            print(f'  filenames:   {" ".join(filenames)}')
        print(f"  contest:     {my_contest['shortname']}")
        print(f"  problem:     {my_problem['label']}")
        print(f"  language:    {my_language['name']}")
        if entry_point:
            print(f'  entry point: {entry_point}')
        print(f'  url:         {baseurl}')

        if num_warnings > 0:
            print('There are warnings for this submission!\a')

        """if not confirm('Do you want to continue?'):
            error('submission aborted by user')"""

    submit_connection = do_api_submit(problem_id, language_id, contest_id, api_version, baseurl, headers, filenames)

    if submit_connection:
        await message.answer('Решение было получено.')
    else:
        await message.answer('Ошибка при отправке решения.')


