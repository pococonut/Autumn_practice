from commands.url_requests import read_teams, USERS_URL_TEMPLATE, CONTESTS_TEAMS_URL_TEMPLATE
from config import settings, admin_authorization
from create import dp
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards import menu_keyboard, registration_ikb


class User(StatesGroup):
    name = State()


def user_registration(name, u_id):
    """
    Функция для регистрации пользователя в системе
    Args:
        name: Имя пользователя
        u_id: Идентификатор пользователя

    Returns: Список - [Сообщение, клавиатура]
    """

    session = admin_authorization(settings.admin_username, settings.admin_password)
    teams = read_teams()
    # Данные новой команды
    unic_name_team = name + "_" + u_id
    new_team_data = {
        "display_name": name,
        "name": unic_name_team,
        "id": str(int(teams[-1].get("id")) + 1),
        "group_ids": ["3"]
    }

    # Отправка POST-запроса для добавления новой команды
    response_team = session.post(CONTESTS_TEAMS_URL_TEMPLATE, json=new_team_data)
    # Проверка статуса ответа
    if response_team.status_code != 201:
        return ["Ошибка сервера.", registration_ikb]

    team_id = None
    for team in read_teams():
        if u_id == team.get("name").split("_")[-1]:
            team_id = team.get("id")

    if not team_id:
        return ["Ошибка сервера.", registration_ikb]

    new_user_data = {
        'username': f"{name}_{u_id}",
        'name': name,
        'password': f"user_{u_id}",
        'enabled': True,
        "team_id": team_id,
        'roles': ['team']
    }

    # Отправка POST-запроса для добавления нового пользователя
    response_user = session.post(USERS_URL_TEMPLATE, json=new_user_data)
    if response_user.status_code != 201:
        return ["Ошибка сервера.", registration_ikb]

    return ["Вы были успешно зарегистрированы.", menu_keyboard]


@dp.callback_query(F.data == "registration")
async def reg_user(callback: types.CallbackQuery, state: FSMContext):
    """
    Функция для регистрации пользователя
    """
    print("registration")
    already_exist = [True for t in read_teams() if str(callback.from_user.id) in t.get("name")]
    if already_exist:
        await callback.message.edit_text("Вы уже зарегистрированы.", reply_markup=menu_keyboard)
    else:
        await callback.message.edit_text("Отправьте ФИО в формате Иванов Иван Иванович.")
        await state.set_state(User.name)


@dp.message(User.name)
async def get_user_name(message: types.Message, state: FSMContext):
    """
    Функция для получения имени пользователя и занесения пользователя в БД
    """

    if len(message.text.split()) != 3 or not message.text.replace(" ", "").replace("-", "").isalpha():
        await message.answer("ФИО введено в некорректном формате, повторите ввод.")
        return

    name = " ".join([w.capitalize() for w in message.text.split()])
    await state.update_data(name=name)
    data = await state.get_data()
    await state.clear()

    result_reg = user_registration(data['name'], str(message.from_user.id))
    await message.answer(result_reg[0], reply_markup=result_reg[1])






