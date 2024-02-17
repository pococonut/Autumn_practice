import requests
from pydantic.v1 import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    api: str = os.getenv("API")
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")


settings = Settings()


def admin_authorization(uname, passw):
    """
    Функция авторизации для пользователя admin
    Args:
        uname: username для пользователя admin
        passw: password для пользователя admin

    Returns: Объект сеанса
    """

    session = requests.Session()
    session.auth = (uname, passw)
    return session
