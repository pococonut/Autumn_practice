from commands.url_requests import read_teams, read_problem_text
import codecs
import os
import textract


def get_lvl_task(el):
    """
    Возвращает уровень задачи
    Args:
        el: Задача
    Returns: Уровень
    """

    levels = {"A": "Легкий",
              "B": "Средний",
              "C": "Сложный"}

    level = el.get('label')
    for k, v in levels.items():
        if k in el.get('label'):
            return v
    return level


def get_solved_problems(resp, u_id):
    """
    Функция для получения информации о команде, пользователе и списка решенных задач
    Args:
        resp: Ответ сервера
        u_id: Идентификатор пользователя

    Returns: Информации о команде, пользователе и список решенных задач
    """

    result = resp.json()
    table = result.get("rows")
    team_info = None
    for t in read_teams():
        if "_" in t.get("name") and str(u_id) == t.get("name").split("_")[1]:
            team_info = t
    info = [t for t in table if t.get("team_id") == team_info.get("id")][0]
    return team_info, info, [p for p in info.get("problems") if p.get("solved")]


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

    level = get_lvl_task(problem)

    s = (f"<b><em>Название:</em></b> {problem.get('name')}\n"
         f"<b><em>Уровень:</em></b> {level}\n"
         f"<b><em>Ограничение по времени:</em></b> {problem.get('time_limit')} сек.\n")

    style_msg = {"Формат входных данных": "\n\n<b><em>Формат входных данных:</em></b>",
                 "Формат выходных данных": "\n\n<b><em>Формат выходных данных:</em></b>",
                 "Примечание": "\n\n<b><em>Примечание</em></b>",
                 "Пример входных данных": "\n\n<b><em>Пример входных данных</em></b>",
                 "Пример выходных данных": "\n\n<b><em>Пример выходных данных</em></b>"
                 }

    response = read_problem_text(problem.get("id"))

    if response.status_code == 200:
        path = f"files/description_problem{problem.get('id')}"
        with open(f"{path}.pdf", "wb") as file:
            file.write(response.content)
            # преобразование файла в текст
            text = codecs.decode(textract.process(f"{path}.pdf"), "UTF-8")

            if not more:
                text = text.split("Формат входных данных")[0]

            text = text.replace('\n', ' ')
            for k, v in style_msg.items():
                if k in text:
                    text = text.replace(k, v)
            text = text.replace(": ", ":\n")

            s += f"<b><em>Описание:</em></b>\n\n{text}"

        os.remove(f"{path}.pdf")
    return s
