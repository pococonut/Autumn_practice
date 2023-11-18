from datetime import date
import requests
from config import settings
from create import dp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards import menu_keyboard


class User(StatesGroup):
    name = State()


@dp.callback_query_handler(text="registration")
async def reg_user(callback: types.CallbackQuery):
    username = settings.admin_username
    password = settings.admin_password
    session = requests.Session()
    session.auth = (username, password)
    url_get_teams = "http://localhost:12345/api/v4/contests/2/teams?strict=false"

    response_get_teams = session.get(url_get_teams)
    already_exist = [True for t in response_get_teams.json() if str(callback.from_user.id) in t.get("name")]
    if already_exist:
        await callback.message.edit_text("Вы уже зарегистрированы.", reply_markup=menu_keyboard)
    else:
        await callback.message.edit_text("Отправьте ваше имя в формате Иван Иванов.")
        await User.name.set()


@dp.message_handler(state=User.name)
async def get_user_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await state.finish()

    username = settings.admin_username
    password = settings.admin_password
    session = requests.Session()
    session.auth = (username, password)

    url_add_user = "http://localhost:12345/api/v4/users"
    url_add_team = "http://localhost:12345/api/v4/contests/2/teams"
    url_get_teams = "http://localhost:12345/api/v4/contests/2/teams?strict=false"

    response_get_teams = session.get(url_get_teams)
    # данные новой команды
    unic_name_team = data['name'] + "_" + str(message.from_user.id)
    new_team_data = {
        "display_name": data["name"],
        "name": unic_name_team,
        "id": str(int(response_get_teams.json()[-1].get("id")) + 1)
    }

    # Отправка POST-запроса для добавления новой команды
    response_team = session.post(url_add_team, json=new_team_data)

    # Проверка статуса ответа
    if response_team.status_code == 201:
        print('Команда успешно успешно добавлена')

        # данные нового пользователя
        password = f"{str(message.from_user.id)}_{str(date.today()).replace('-','_')}"

        response_get_teams = session.get(url_get_teams)
        team_id = None
        for team in response_get_teams.json():
            print(team.get("name"))
            if str(message.from_user.id) == team.get("name").split("_")[-1]:
                print(str(message.from_user.id), team.get('name').split("_")[-1])
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

            # Отправка POST-запроса для добавления новой команды
            response_user = session.post(url_add_user, json=new_user_data)

            if response_user.status_code == 201:
                await message.answer("Вы были успешно зарегистрированы.", reply_markup=menu_keyboard)
            else:
                await message.answer("Ошибка сервера.")
                print(response_user.text)

        else:
            await message.answer("Ошибка сервера.")
    else:
        await message.answer('Ошибка сервера.')
        print(response_team.text)





