import requests
import requests.utils
import base64
from commands.get_tasks import problemIdDict
from commands.url_requests import do_api_submit, CONTEST_ID, read_users
from create import dp, bot
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from config import settings
from keyboards import languages_ikb, back_ikb, check_result_ikb


solutionsID = {}
previous_messages = {}


class File(StatesGroup):
    lang = State()
    file = State()


async def download_file(filename, file_id):
    """
    Функция для скачивания файла с решением
    Args:
        filename: Название файла
        file_id: ID файла
    """

    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    file_url = f"https://api.telegram.org/file/bot{settings.api}/{file_path}"
    # Скачиваем файл
    response = requests.get(file_url)
    # Сохраняем файл на локальном компьютере
    with open(filename, 'wb') as f:
        f.write(response.content)


@dp.callback_query_handler(text=['solution'])
async def wait_file(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите язык.", reply_markup=languages_ikb)
    await File.lang.set()


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

    problem_id = problemIdDict[f'{message.from_user.id}']
    data = await state.get_data()
    await state.finish()

    # Получаем информацию о файле
    filename = f'files/solutions/solution_{CONTEST_ID}_{problem_id}_{message.from_user.id}.{data["lang"][1]}'
    file_id = message.document.file_id
    # Скачиваем и сохраняем файл
    await download_file(filename, file_id)
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=previous_messages[str(message.from_user.id)])

    language_id = data["lang"][0]
    password = f"user_{str(message.from_user.id)}"
    filenames = [f'{filename}']
    for u in read_users():
        if str(message.from_user.id) == u.get("username").split("_")[-1]:
            print(u)
            username = u.get("username")
            break

    headers = {'user-agent': f'domjudge-submit-client ({requests.utils.default_user_agent()})'}
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers['Authorization'] = f'Basic {credentials}'

    submit_connection, data = do_api_submit(problem_id, language_id, headers, filenames)

    if submit_connection:
        await message.answer('Решение было получено.', reply_markup=check_result_ikb)
        solutionsID[message.from_user.id] = data
    else:
        await message.answer(f'Ошибка при отправке решения: {data}.')


