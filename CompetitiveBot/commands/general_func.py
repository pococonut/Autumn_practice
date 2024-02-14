import json
import os
import logging
import fitz
from commands.url_requests import read_problem_text


def read_user_values(dict_name):
    """
    Функция для чтения переменных пользователя, используемых при взаимодействии с ботом
    Args:
        dict_name: Название словаря с переменными

    Returns: Словарь с переменными
    """

    filename = "user_values.json"
    try:
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='UTF-8') as f:
                json.dump({}, f)

        with open(filename, 'r', encoding='UTF-8') as file:
            data = json.load(file)
            g_dict = data.get(f'{dict_name}', {})
            return g_dict

    except FileNotFoundError:
        logging.warning(f"File {filename} not found.")
        return {}
    except json.JSONDecodeError:
        logging.warning(f"Error decoding JSON from file {filename}.")
        return {}


def write_user_values(dict_name, g_dict):
    """
    Функция для записи переменных пользователя, используемых при взаимодействии с ботом
    Args:
        dict_name: Название словаря с переменными
        g_dict: Словарь с переменными

    Returns: None
    """

    filename = "user_values.json"
    try:
        with open(filename, 'r', encoding='UTF-8') as file:
            data = json.load(file)
            data[f'{dict_name}'] = g_dict

        with open(filename, 'w', encoding='UTF-8') as file:
            json.dump(data, file)
    except Exception as e:
        logging.exception(e)


def get_page(user_id, global_dict_move, tasks_lst):
    """
    Функция возвращающая номер просматриваемой задачи из общего количества задач
    Args:
        user_id: Идентификатор пользователя в телеграм
        global_dict_move: Словарь с номером текущей страницей задачи
        tasks_lst: Список задач

    Returns: номер просматриваемой задачи
    """

    page = global_dict_move[user_id]
    if global_dict_move[user_id] <= -1:
        page = len(tasks_lst) + global_dict_move[user_id]

    return page


def get_lvl_task(task):
    """
    Функция возвращает уровень задачи
    Args:
        task: Задача
    Returns: Уровень
    """

    possible_levels = {"A": "Легкий", "B": "Средний", "C": "Сложный"}
    current_task_level = task.get('label')

    for label, value in possible_levels.items():
        if label in task.get('label'):
            return value

    return current_task_level


def navigation(direction, page, count):
    """
    Функция для навигации по списку объектов
    Args:
        direction: Направление (Вперед, Назад)
        page: Номер объекта из всего списка
        count: Количество объектов

    Returns: Строка с номером объекта из общего количества, Номер объекта
    """

    s = ''
    if 'right' in direction:
        page += 1
        if page == count:
            page = 0
        num = page
        if page <= -1:
            num = count + page
        s = f"<b>№</b> {num + 1}/{count}\n\n"

    elif 'left' in direction:
        page -= 1
        num = 0
        if page == (-1) * count:
            page = 0
        if page <= -1:
            num = count
        s = f"<b>№</b> {(num + page) + 1}/{count}\n\n"

    return s, page


def get_text_task_description(task_data):
    """
    Функция переводит описание задачи из pdf в текст
    Args:
        task_data: Описание задачи

    Returns: Описание задачи в текстовом формате
    """

    problem_text_pdf = fitz.open("pdf", task_data)
    text = ""
    # Извлечение текста из каждой страницы PDF и добавление его к переменной text
    for page_number in range(problem_text_pdf.page_count):
        page = problem_text_pdf.load_page(page_number)
        text += page.get_text("text")
    return text


def add_style_text(text):
    """
    Функция для выделения дополнительных параметров задачи
    Args:
        text: Описание задачи в текстовом формате

    Returns: Описание задачи
    """

    other_params = {"Формат входных данных": "\n\n<b><em>Формат входных данных:</em></b>",
                    "Формат выходных данных": "\n\n<b><em>Формат выходных данных:</em></b>",
                    "Примечание": "\n\n<b><em>Примечание</em></b>",
                    "Пример входных данных": "\n\n<b><em>Пример входных данных</em></b>",
                    "Пример выходных данных": "\n\n<b><em>Пример выходных данных</em></b>"}

    text = text.replace('\n', ' ')
    for param, style_param in other_params.items():
        if param in text:
            text = text.replace(param, style_param)
    return text.replace(": ", ":\n")


def print_task(problem, more=0):
    """
    Функция печати данных задачи.
    Args:
        more: Параметр для краткого показа задачи - 0,
              подробного показа задачи - 1
        problem: Словарь с параметрами задачи

    Returns: Строка с информацией о задаче
    """

    task_description = (f"<b><em>Название:</em></b> {problem.get('name')}\n"
                        f"<b><em>Уровень:</em></b> {get_lvl_task(problem)}\n"
                        f"<b><em>Ограничение по времени:</em></b> "
                        f"{problem.get('time_limit')} сек.\n")

    response = read_problem_text(problem.get("id"))

    if response.status_code == 200:
        text = get_text_task_description(response.content)
        if not more:
            text = text.split("Формат входных данных")[0]

        style_text_text = add_style_text(text)
        task_description += f"<b><em>Описание:</em></b>\n\n{style_text_text}"

    return task_description
