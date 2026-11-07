from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    database_url: PostgresDsn = PostgresDsn(
        url="postgresql+psycopg2://postgres:postgres@0.0.0.0:5432/postgres"
    )


settings = AppSettings()
