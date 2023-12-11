from commands.url_requests import read_teams, USERS_URL_TEMPLATE, CONTESTS_TEAMS_URL_TEMPLATE
from config import settings, admin_authorization
from create import dp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards import menu_keyboard


class User(StatesGroup):
    name = State()


@dp.callback_query_handler(text="registration")
async def reg_user(callback: types.CallbackQuery):
    """
    Функция начала регистрации пользователя
    """
    already_exist = [True for t in read_teams() if str(callback.from_user.id) in t.get("name")]
    if already_exist:
        await callback.message.edit_text("Вы уже зарегистрированы.", reply_markup=menu_keyboard)
    else:
        await callback.message.edit_text("Отправьте ФИО в формате Иванов Иван Иванович.")
        await User.name.set()


@dp.message_handler(state=User.name)
async def get_user_name(message: types.Message, state: FSMContext):
    """
    Функция получения имени пользователя и занесения пользователя в БД
    """
    if len(message.text.split()) != 3 or not message.text.replace(" ", "").replace("-", "").isalpha():
        await message.answer("ФИО введено в некорректном формате, повторите ввод.")
        return

    name = " ".join([w.capitalize() for w in message.text.split()])
    await state.update_data(name=name)
    data = await state.get_data()
    await state.finish()

    session = admin_authorization(settings.admin_username, settings.admin_password)
    teams = read_teams()
    # Данные новой команды
    unic_name_team = data['name'] + "_" + str(message.from_user.id)
    new_team_data = {
        "display_name": data["name"],
        "name": unic_name_team,
        "id": str(int(teams[-1].get("id")) + 1),
        "group_ids": ["3"]
    }

    # Отправка POST-запроса для добавления новой команды
    response_team = session.post(CONTESTS_TEAMS_URL_TEMPLATE, json=new_team_data)
    # Проверка статуса ответа
    if response_team.status_code == 201:
        # Данные нового пользователя
        password = f"user_{str(message.from_user.id)}"
        team_id = None
        for team in read_teams():
            if str(message.from_user.id) == team.get("name").split("_")[-1]:
                team_id = team.get("id")

        if team_id:
            new_user_data = {
                'username': f"{data['name']}_{str(message.from_user.id)}",
                'name': data["name"],
                'password': password,
                'enabled': True,
                "team_id": team_id,
                'roles': ['team']
            }

            # Отправка POST-запроса для добавления нового пользователя
            response_user = session.post(USERS_URL_TEMPLATE, json=new_user_data)
            if response_user.status_code == 201:
                await message.answer("Вы были успешно зарегистрированы.", reply_markup=menu_keyboard)
            else:
                await message.answer("Ошибка сервера.")
        else:
            await message.answer("Ошибка сервера.")
    else:
        await message.answer('Ошибка сервера.')





