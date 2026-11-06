from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    name: str = "Sample API"


settings = AppSettings()
