import requests
from config import settings

USERNAME = settings.admin_username
PASSWORD = settings.admin_password

# Создаем объект сеанса
session = requests.Session()
# Выполняем проверку подлинности
session.auth = (USERNAME, PASSWORD)

url_add_usr = "http://localhost:12345/api/v4/users"
url_add_team = "http://localhost:12345/api/v4/contests/2/teams"

# данные новой команды
new_team_data = {
    'display_name': 'TEST_TEAM2',
    'name': 'test_team2',
    "id": "test2"
}

# данные нового пользователя
new_user_data = {
    'username': 'test4',
    'name': 'Иван Иванов',
    'email': 'ivan@example.com',
    'password': '1234567890',
    'enabled': True,
    "team_id": "3",
    'roles': ['team']
}

# Отправка POST-запроса для добавления новой команды
response = session.post(url_add_team, json=new_team_data)

# Проверка статуса ответа
if response.status_code == 201:
    print('Команда успешно успешно добавлена')
else:
    print('Ошибка при добавлении команды:', response.text)


# Отправка POST-запроса для добавления нового пользователя
response = session.post(url_add_usr, json=new_user_data)

# Проверка статуса ответа
if response.status_code == 201:
    print('Пользователь успешно добавлен')
else:
    print('Ошибка при добавлении пользователя:', response.text)
