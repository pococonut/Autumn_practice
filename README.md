
# CompetitiveBot

## Описание проекта

CompetitiveBot - это телеграм бот, предоставляющий возможности соревновательной системы по программированию на основе сервиса DOMjudge. CompetitiveBot предоставляет список доступных задач по программированию трех уровней сложности. Решения принимаются на нескольких доступных языках, благодаря чему, вы можете проверить свои навыки в каждом из них. Также бот выводит рейтинговую таблицу, где вы можете увидеть свое место среди других пользователей. Это поможет вам отслеживать свой прогресс и стремиться к новым результатам.


CompetitiveBot объеденяет в себе разработанный интерфейс в виде телеграм-бота, серверную часть, предоставляющую веб-интерфейс для работы с данными (domserver), сервер судьи, необходимый для оценки и тестирования решений пользователей (judgehost) и базу данных

## Руководство по установке и настройке сервиса CompetitiveBot

### Установка необходимых контейнеров и исходного кода проекта.

При установке используются образы docker и код проекта из github. Для проекта была использована ОС Ubuntu 20.04.

1. Установка docker.
\
Руководство по установке dpcker вы можете найти на [странице официальной документации](https://docs.docker.com/engine/install/ubuntu/).

2. Установка контейнера базы данных.
\
MariaDB container:

```
sudo docker run -it --name dj-mariadb -e MYSQL_ROOT_PASSWORD=rootpw -e MYSQL_USER=domjudge -e MYSQL_PASSWORD=djpw -e MYSQL_DATABASE=domjudge -p 13306:3306 mariadb --max-connections=1000
```

3. Установка контейнера сервера.
\
DOMserver container:

```
docker run --link dj-mariadb:mariadb -it -e MYSQL_HOST=mariadb -e MYSQL_USER=domjudge -e MYSQL_DATABASE=domjudge -e MYSQL_PASSWORD=djpw -e MYSQL_ROOT_PASSWORD=rootpw -p 12345:80 --name domserver domjudge/domserver:latest
```

После установки DOMserver, в консоль будут выведены пароли для пользователей admin и judgehost, их необходимо сохранить, будтье внимательны.

Так же их можно будет найти используя:

```
docker exec -it domserver cat /opt/domjudge/domserver/etc/initial_admin_password.secret
docker exec -it domserver cat /opt/domjudge/domserver/etc/restapi.secret
```

4. Установка контейнера судьи.
\
Внимание, В ключе JUDGEDAEMON_PASSWORD необходимо будет указать пароль judgehost.

Judgehost container:

```
sudo docker run -itd --privileged -v /sys/fs/cgroup:/sys/fs/cgroup:ro --name judgehost-0 --link domserver:domserver --hostname judgedaemon-0 -e DAEMON_ID=0 -e CONTAINER_TIMEZONE=Asia/Shanghai -e JUDGEDAEMON_PASSWORD= domjudge/judgehost:8.2.1
```

5. Клонирование проекта CompetitiveBot из репозитория.

Вы можете это сделать используя

```
git clone https://github.com/pococonut/CompetitiveBot.git
```

6. Создание виртуального окружения.
\
В среде PyCharm:

```
Settings -> Project: CompetitiveBot -> Python Interpreter -> Python 3.x
```

7. Установка необходимых библиотек.
\
Откройте косоль в корневой папке проекта и выполните команду:
```
pip install -r requirements.txt
```
При возникновении ошибок в связи с особенностями вашей системы, будет необходимо исправить их самостоятельно.

8. Создание файла config.py 
\
Для правильной работы программы и ее взаимодействия с другими сервисами, необходимо в корневой папке проекта указать данные в файле config.py.

Пример файла config.py:

```
import requests
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    api: str = "TOKEN"
    admin_username = "admin" # Данное поле можно оставить без изменений, если вы не указывали другого имени для пользователя admin
    admin_password = "ADMIN_PASSWORD"


settings = Settings()


def admin_authorization(uname, passw):
    session = requests.Session()
    session.auth = (uname, passw)
    return session
```

9. Запуск контейнеров

```
docker start dj-mariadb
docker start domserver
docker start judgehost-0
```

После правильной установки, вам будет доступен веб-интерфейс DOMjudge по адресу http://localhost:12345, для входа нужно будет указать имя и пароль пользователя admin.

![веб-интерфейс DOMjudge](images/снимок1.png)




