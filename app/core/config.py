from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    url: PostgresDsn = PostgresDsn(
        url="postgresql+psycopg2://postgres:postgres@0.0.0.0:5432/postgres"
    )
    pool_size: int = 10
    pool_recycle: int = 3600  # Recycle connections every hour


class AppSettings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()


settings = AppSettings()
