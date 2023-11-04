import codecs
import requests
import textract
from create import dp
from aiogram import types
from keyboards import tasks_navigation, menu_keyboard

globalDict = dict()


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


def print_task(problem, c_id):
    """
    Функция печати данных задачи.
    Args:
        problem: Словарь с параметрами задачи
        c_id: Идентификатор соревнования

    Returns: Строка с информацией о задаче
    """
    s = (f"<em>Название:</em> {problem.get('name')}\n"
         f"<em>Уровень:</em> {problem.get('label')}\n"
         f"<em>Ограничение по времени:</em> {problem.get('time_limit')} сек.\n")

    url_problem_text = f'http://localhost:12345/api/v4/contests/{c_id}/problems/{problem.get("id")}/statement?strict=false'
    response = requests.get(url_problem_text)

    if response.status_code == 200:
        with open(f"files/test{problem.get('id')}.pdf", "wb") as file:
            file.write(response.content)
            # преобразование файла в текст
            text = codecs.decode(textract.process(f"files/test{problem.get('id')}.pdf"), "UTF-8")
            s += f"<em>Описание:</em>\n\n{text}"
    return s


@dp.callback_query_handler(text=['tasks', 'left_task', 'right_task'])
async def show_tasks(callback: types.CallbackQuery):
    """
    Функция просмотра доступных задач.
    """
    usr_id = str(callback.from_user.id)
    if usr_id not in globalDict:
        globalDict[usr_id] = 0

    contests_id = 2
    url_problems = f'http://localhost:12345/api/v4/contests/{contests_id}/problems'
    response = requests.get(url_problems)
    tasks = response.json()

    if response.status_code != 200:
        await callback.message.edit_text(f'Ошибка при отправке запроса: {tasks}',
                                         parse_mode='HTML',
                                         reply_markup=tasks_navigation,
                                         disable_web_page_preview=True)
    else:
        if not tasks:
            await callback.message.edit_text('В данный момент задач нет.\nЗагляните позже.', reply_markup=menu_keyboard)
            await callback.answer()
        else:
            count_tasks = len(tasks)
            if callback.data == 'tasks':
                p = globalDict[usr_id]
                if globalDict[usr_id] <= -1:
                    p = count_tasks + globalDict[usr_id]

                await callback.message.edit_text(
                    f"<b>№</b> {p + 1}/{count_tasks}\n\n" + print_task(tasks[globalDict[usr_id]], contests_id),
                    parse_mode='HTML',
                    reply_markup=tasks_navigation,
                    disable_web_page_preview=True)
            else:
                s, globalDict[usr_id] = navigation(callback.data, globalDict[usr_id], count_tasks)
                print(s, globalDict[usr_id])
                await callback.message.edit_text(s + print_task(tasks[globalDict[usr_id]], contests_id),
                                                 parse_mode='HTML',
                                                 reply_markup=tasks_navigation,
                                                 disable_web_page_preview=True)



