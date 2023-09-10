import requests
import json
# Установите ваш API-ключ PythonAnywhere

# Установите URL-адрес API PythonAnywhere
api_url = 'https://www.pythonanywhere.com/api/v0/user/{username}/consoles/{console_id}/send_input/'

# Установите ваше имя пользователя PythonAnywhere и идентификатор консоли
username = 'pococonut000'
console_id = '30126219'

# Установите ваш код для отправки на сервер PythonAnywher


api_key = '44672acb6cfd2928c7525cb5afd3176a4ce1c5b5'
code = '''
x = 1
x += 1
print(x)
'''

url = 'https://www.pythonanywhere.com/api/v0/user/pococonut000/consoles/30126219/send_input/'
headers = {'Authorization': 'Token {0}'.format(api_key)}
data = {'input': code}
response = requests.post(url, headers=headers, data=data)

if response.status_code == 200:
       result = response.json()
       if result['status'] == 'OK':
           print(result)
       else:
           error_message = result['error']
           print('Ошибка выполнения программы:', error_message)
else:
       print('Ошибка при отправке запроса:', response.status_code)


username = 'pococonut000'
token = '44672acb6cfd2928c7525cb5afd3176a4ce1c5b5'
response = requests.get(
    'https://www.pythonanywhere.com/api/v0/user/{username}/consoles/30126219/get_latest_output/'.format(
        username=username
    ),
    headers={'Authorization': 'Token {token}'.format(token=token)}
)
if response.status_code == 200:
    print('CPU quota info:')
    r = eval(response.content.decode("utf-8"))
    result = r['output'].split('>>>')[-2]
    if 'Error' in result:
        print("Вы допустили ошибку:\n")
        print(result)
    else:
        if result == 2:
            print("Правильно:")
        else:
            print('Вывод программы не верный:')
            print(result)

else:
    print('Got unexpected status code {}: {!r}'.format(response.status_code, response.content))