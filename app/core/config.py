from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    name: str = "Sample API"
    database_url: PostgresDsn = PostgresDsn(
        url="postgresql+psycopg2://postgres:postgres@0.0.0.0:5432/postgres"
    )


settings = AppSettings()
