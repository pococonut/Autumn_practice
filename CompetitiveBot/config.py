from pydantic import BaseSettings


class Settings(BaseSettings):
    api: str = "6425974331:AAGkpc0QvdHdkkijLeg3neC6GcRiCnosgbM"
    #host: str = "localhost"
    #password: str = "123"
    #database: str = "bot"


settings = Settings()