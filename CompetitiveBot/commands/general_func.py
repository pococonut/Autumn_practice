import fitz
from commands.url_requests import read_problem_text
import json
import os
import logging


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
            with open(filename, 'w') as f:
                json.dump({}, f)

        with open(filename, 'r') as file:
            data = json.load(file)
            g_dict = data.get(f'{dict_name}', {})
            return g_dict

    except FileNotFoundError:
        logging.warning(f"File {filename} not found.")
    except json.JSONDecodeError:
        logging.warning(f"Error decoding JSON from file {filename}.")


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
        with open(filename, 'r') as file:
            data = json.load(file)
            data[f'{dict_name}'] = g_dict

        with open(filename, 'w') as file:
            json.dump(data, file)
    except Exception as e:
        logging.warning(e)


def get_page(u_id, global_dict_move, lst):
    """
    Функция возвращающая номер просматриваемой задачи из общего количества задач
    Args:
        u_id: Идентификатор пользователя
        global_dict_move: Словарь с номером текущей страницей задачи
        lst: Список задач

    Returns: номер просматриваемой задачи
    """

    p = global_dict_move[u_id]
    if global_dict_move[u_id] <= -1:
        p = len(lst) + global_dict_move[u_id]

    return p


def get_lvl_task(el):
    """
    Возвращает уровень задачи
    Args:
        el: Задача
    Returns: Уровень
    """

    levels = {"A": "Легкий", "B": "Средний", "C": "Сложный"}
    level = el.get('label')

    for k, v in levels.items():
        if k in el.get('label'):
            return v

    return level


def navigation(direction, page, count):
    """
    Функция для навигации по списку объектов.
    :param direction: Направление (Вперед, Назад).
    :param page: Текущая номер объекта.
    :param count: Количество объектов.
    :return: Строка, Номер объекта.
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


def print_task(problem, more=0):
    """
    Функция печати данных задачи.
    Args:
        more: Параметр для краткого - 0, подробного - 1 показа задачи
        problem: Словарь с параметрами задачи

    Returns: Строка с информацией о задаче
    """

    s = (f"<b><em>Название:</em></b> {problem.get('name')}\n"
         f"<b><em>Уровень:</em></b> {get_lvl_task(problem)}\n"
         f"<b><em>Ограничение по времени:</em></b> {problem.get('time_limit')} сек.\n")

    style_msg = {"Формат входных данных": "\n\n<b><em>Формат входных данных:</em></b>",
                 "Формат выходных данных": "\n\n<b><em>Формат выходных данных:</em></b>",
                 "Примечание": "\n\n<b><em>Примечание</em></b>",
                 "Пример входных данных": "\n\n<b><em>Пример входных данных</em></b>",
                 "Пример выходных данных": "\n\n<b><em>Пример выходных данных</em></b>"
                 }

    response = read_problem_text(problem.get("id"))

    if response.status_code == 200:
        pdf_document = fitz.open("pdf", response.content)
        text = ""
        # Извлечение текста из каждой страницы PDF и добавление его к переменной text
        for page_number in range(pdf_document.page_count):
            page = pdf_document.load_page(page_number)
            text += page.get_text("text")

        if not more:
            text = text.split("Формат входных данных")[0]

        text = text.replace('\n', ' ')
        for k, v in style_msg.items():
            if k in text:
                text = text.replace(k, v)
        text = text.replace(": ", ":\n")

        s += f"<b><em>Описание:</em></b>\n\n{text}"

    return s
