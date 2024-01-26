from commands.url_requests import read_teams


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
