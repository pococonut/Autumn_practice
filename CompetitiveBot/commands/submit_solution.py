import tempfile
import requests
import requests.utils
import base64
from commands.general_func import print_task, read_user_values, write_user_values
from commands.get_tasks import globalDict_task
from commands.menu import global_Dict_del_msg
from commands.url_requests import do_api_submit, read_users, read_problems
from create import dp, bot
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards import languages_ikb, back_ikb, check_result_ikb, menu_keyboard

globalDict_solutions = read_user_values("globalDict_solutions")
globalDict_prev_msg = read_user_values("globalDict_prev_msg")


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

    tasks_lst = read_problems()
    if not tasks_lst:
        await callback.message.edit_text("Ошибка сервера.")
        await callback.answer()
    else:
        problem = [t for t in tasks_lst if t.get("id") == globalDict_task[f'{str(callback.from_user.id)}']][0]
        text = print_task(problem).split("<b><em>Описание:</em></b>")[0]
        await callback.message.edit_text(text + "\nВыберите язык.", reply_markup=languages_ikb)
        await state.set_state(File.lang)


@dp.callback_query(File.lang)
async def get_lang_file(callback: types.CallbackQuery, state: FSMContext):
    """
    Функция для выбора языка для отправки решения.
    """
    if callback.data == "back":
        await state.clear()
        await callback.message.edit_reply_markup()
        await callback.message.edit_text('Действие отменено.')
    else:
        languages_id = {"lang_C": ["c", "c"],
                        "lang_C++": ["cpp", "cpp"],
                        "lang_Java": ["java", "java"],
                        "lang_Python": ["python3", "py"]}
        await state.update_data(lang=languages_id[callback.data])
        await callback.message.edit_text("Отправьте файл с решением.", reply_markup=back_ikb)
        globalDict_prev_msg[callback.from_user.id] = callback.message.message_id
        write_user_values("globalDict_prev_msg", globalDict_prev_msg)


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
        await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=globalDict_prev_msg[int(u_id)])

        submit_connection, submission_id = send_file(u_id, data["lang"][0], filename)
        if submit_connection:
            sent_msg = await message.answer('Решение было получено.', reply_markup=check_result_ikb)
            globalDict_solutions[u_id] = submission_id
            global_Dict_del_msg[u_id] = sent_msg.message_id
            write_user_values("globalDict_solutions", globalDict_solutions)
            write_user_values("global_Dict_del_msg", global_Dict_del_msg)

        else:
            sent_msg = await message.answer(f'Ошибка при отправке файла.', reply_markup=menu_keyboard)
            global_Dict_del_msg[u_id] = sent_msg.message_id
            write_user_values("global_Dict_del_msg", global_Dict_del_msg)
