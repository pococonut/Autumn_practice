import tempfile
import base64
import requests
import requests.utils
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from create import dp, bot
from commands.general_func import print_task, read_user_values, write_user_values
from commands.get_tasks import globalDict_task
from commands.menu import global_Dict_del_msg
from commands.url_requests import do_api_submit, read_users, read_problems
from keyboards import languages_ikb, back_ikb, check_result_ikb, menu_keyboard, menu_ikb

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


def send_file(usr_id, language_id, filename):
    """
    Функция для отправки решения на сервер
    Args:
        usr_id: Идентификатор пользователя
        language_id: Идентификатор языка программирования
        filename: Путь к файлу с решением

    Returns: Ответ севера, идентификатор решения
    """

    username = ""
    problem_id = globalDict_task[f'{usr_id}']
    password = f"user_{usr_id}"
    filenames = [f'{filename}']

    for user in read_users():
        if usr_id == user.get("username").split("_")[-1]:
            username = user.get("username")
            break

    headers = {'user-agent': f'domjudge-submit-client ({requests.utils.default_user_agent()})'}
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers['Authorization'] = f'Basic {credentials}'

    return do_api_submit(problem_id, language_id, headers, filenames)


def get_curr_task_submission(tasks, usr_id):
    """
    Функция получения текущей задачи, для отправки решения на нее
    Args:
        tasks: Список задач
        usr_id: Идентификатор пользователя в телеграм

    Returns: Задача, на которую пользователь хочет отправить решение
    """

    for task in tasks:
        if task.get("id") == globalDict_task[usr_id]:
            return task


def get_result_sending_file(usr_id, s_id, s_connection):
    """
    Функция для получения результата отправки решения задачи
    Args:
        usr_id: Идентификатор пользователя в телеграм
        s_id: Идентификатор решения
        s_connection: Соединение

    Returns: Сообщение и клавиатура в зависимости от
             того, было ли получено решение на сервере
    """

    if s_connection:
        globalDict_solutions[usr_id] = s_id
        write_user_values("globalDict_solutions", globalDict_solutions)
        return 'Решение было получено.', check_result_ikb
    return 'Ошибка при отправке файла.', menu_keyboard


@dp.callback_query(F.data == 'solution')
async def choose_lang_file(callback: types.CallbackQuery, state: FSMContext):
    """
    Функция начала отправки решения
    """

    tasks = read_problems()
    if not tasks:
        await callback.message.edit_text("Ошибка сервера.")
        await callback.answer()
    else:
        usr_id = str(callback.from_user.id)
        problem = get_curr_task_submission(tasks, usr_id)
        text = print_task(problem).split("<b><em>Описание:</em></b>")[0] + "\nВыберите язык."
        await callback.message.edit_text(text, reply_markup=languages_ikb)
        await state.set_state(File.lang)


@dp.callback_query(File.lang)
async def get_lang_file(callback: types.CallbackQuery, state: FSMContext):
    """
    Функция выбора языка для отправки решения
    """

    if callback.data == "back":
        await state.clear()
        await callback.message.edit_reply_markup()
        sent_msg = await callback.message.edit_text('Действие отменено.', reply_markup=menu_ikb)
        global_Dict_del_msg[str(callback.from_user.id)] = sent_msg.message_id
        write_user_values("global_Dict_del_msg", global_Dict_del_msg)
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
    Функция для отправки решения на сервер
    """

    usr_id = str(message.from_user.id)
    data = await state.get_data()

    if not data:
        text, keyboard = 'Ошибка при отправке файла.', menu_keyboard
    else:
        await state.clear()
        # Сохраняем файл
        filename = await save_file(message.document.file_id, data["lang"][1])
        # Удаляем кнопку отмены отправки файла
        msg_id = globalDict_prev_msg[int(usr_id)]
        await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=msg_id)

        submit_connection, submission_id = send_file(usr_id, data["lang"][0], filename)
        text, keyboard = get_result_sending_file(usr_id, submission_id, submit_connection)

    sent_msg = await message.answer(text, reply_markup=keyboard)
    global_Dict_del_msg[usr_id] = sent_msg.message_id
    write_user_values("global_Dict_del_msg", global_Dict_del_msg)
