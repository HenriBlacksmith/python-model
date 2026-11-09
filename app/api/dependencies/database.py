from typing import Annotated
lazy from collections.abc import Generator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.adapters.database.adapter import DatastoreAdapter


def _get_session(request: Request) -> Generator[Session]:
    with Session(request.state.database_engine) as session:
        yield session


DatabaseSessionDepends = Annotated[Session, Depends(_get_session)]


def get_database_adapter(session: DatabaseSessionDepends) -> DatastoreAdapter:
    return DatastoreAdapter(session=session)


DatabaseAdapterDepends = Annotated[DatastoreAdapter, Depends(get_database_adapter)]
