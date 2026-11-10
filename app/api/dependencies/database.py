from typing import Annotated
lazy from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.adapter import DatastoreAdapter


async def _get_session(request: Request) -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(request.state.database_engine) as session:
        yield session


DatabaseSessionDepends = Annotated[AsyncSession, Depends(_get_session)]


def get_database_adapter(session: DatabaseSessionDepends) -> DatastoreAdapter:
    return DatastoreAdapter(session=session)


DatabaseAdapterDepends = Annotated[DatastoreAdapter, Depends(get_database_adapter)]
