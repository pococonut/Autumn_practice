import requests

# Список доступных языков
url4 = 'http://localhost:12345/api/v4/languages?strict=false'

response = requests.get(url4)
result = response.json()

if response.status_code == 200:
    print(result)
else:
       print('Ошибка при отправке запроса:', result)
