from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.adapters.database.adapter import DatastoreAdapter
from app.core.config import settings

connect_args = {}
engine = create_engine(
    settings.database_url.unicode_string(), connect_args=connect_args
)


def _get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session


DatabaseSessionDepends = Annotated[Session, Depends(_get_session)]


def get_database_adapter(session: DatabaseSessionDepends) -> DatastoreAdapter:
    return DatastoreAdapter(session=session)


DatabaseAdapterDepends = Annotated[DatastoreAdapter, Depends(get_database_adapter)]
