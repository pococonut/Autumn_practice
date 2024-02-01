import tempfile
import requests
import requests.utils
import base64
from commands.get_tasks import globalDict_task
from commands.url_requests import do_api_submit, read_users
from create import dp, bot
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards import languages_ikb, back_ikb, check_result_ikb, menu_keyboard

globalDict_solutions = {}
globalDict_prev_msg = {}


class File(StatesGroup):
    lang = State()


async def save_file(file_id, lang):
    """
    Функция сохранения файла с решением в виде временного файла
    Args:
        file_id: Идентификатор файла
        lang: расширение файла программы в соответствии с языком на котором она написана

    Returns: Временный путь файла
    """
    file_info = await bot.get_file(file_id)
    file_bytes = await bot.download_file(file_info.file_path)
    # Создаем временный файл и записываем в него содержимое file_bytes
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'{lang}') as temp_file:
        temp_file.write(file_bytes.getvalue())
        filename = temp_file.name
    return filename


def send_file(u_id, language_id, filename):
    """
    Функция для отправки решения на сервер
    Args:
        u_id: Идентификатор пользователя
        language_id: Идентификатор языка программирования
        filename: Путь к файлу с решением

    Returns: Ответ севера, идентификатор решения
    """

    username = ""
    problem_id = globalDict_task[f'{u_id}']
    password = f"user_{u_id}"
    filenames = [f'{filename}']
    for u in read_users():
        if u_id == u.get("username").split("_")[-1]:
            username = u.get("username")
            break

    headers = {'user-agent': f'domjudge-submit-client ({requests.utils.default_user_agent()})'}
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers['Authorization'] = f'Basic {credentials}'

    return do_api_submit(problem_id, language_id, headers, filenames)


@dp.callback_query(F.data == 'solution')
async def choose_lang_file(callback: types.CallbackQuery, state: FSMContext):
    """
    Функция начала отправки решения.
    """

    await callback.message.edit_text("Выберите язык.", reply_markup=languages_ikb)
    await state.set_state(File.lang)


@dp.callback_query(File.lang)
async def get_lang_file(callback: types.CallbackQuery, state: FSMContext):
    """
    Функция для выбора языка для отправки решения.
    """
    if callback.data == "back":
        await state.clear()
        await callback.message.edit_reply_markup()
        keyboard = menu_keyboard
        await callback.message.edit_text('Действие отменено.', reply_markup=keyboard)
    else:
        languages_id = {"lang_C": ["c", "c"],
                        "lang_C++": ["cpp", "cpp"],
                        "lang_Java": ["java", "java"],
                        "lang_Python": ["python3", "py"]}
        await state.update_data(lang=languages_id[callback.data])
        await callback.message.edit_text("Отправьте файл с решением.", reply_markup=back_ikb)
        globalDict_prev_msg[str(callback.from_user.id)] = callback.message.message_id


@dp.message(F.content_type == types.ContentType.DOCUMENT)
async def handle_document(message: types.Message, state: FSMContext):
    """
    Функция для отправки решения на сервер.
    """
    data = await state.get_data()
    if data:
        u_id = str(message.from_user.id)
        await state.clear()
        # Сохраняем файл
        filename = await save_file(message.document.file_id, data["lang"][1])
        # Удаляем кнопку отмены отправки файла
        await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=globalDict_prev_msg[u_id])

        submit_connection, submission_id = send_file(u_id, data["lang"][0], filename)
        if submit_connection:
            await message.answer('Решение было получено.', reply_markup=check_result_ikb)
            globalDict_solutions[int(u_id)] = submission_id
        else:
            await message.answer(f'Ошибка при отправке файла.', reply_markup=menu_keyboard)
