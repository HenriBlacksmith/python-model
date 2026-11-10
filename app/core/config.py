import os
from typing import Annotated

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)
lazy from pydantic import Field, PostgresDsn

config_file_path = os.getenv("CONFIG_FILE_PATH", "config.yaml")


class DatabaseSettings(BaseSettings):
    url: PostgresDsn
    pool_size: int = 10
    pool_recycle: int = 3600  # Recycle connections every hour


class AppSettings(BaseSettings):
    database: Annotated[DatabaseSettings, Field(alias="database")]

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,  # ruff: ignore[ARG003]
        env_settings: PydanticBaseSettingsSource,  # ruff: ignore[ARG003]
        dotenv_settings: PydanticBaseSettingsSource,  # ruff: ignore[ARG003]
        file_secret_settings: PydanticBaseSettingsSource,  # ruff: ignore[ARG003]
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls, yaml_file=config_file_path),)


settings = AppSettings()
