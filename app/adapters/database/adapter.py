lazy from uuid import UUID

from sqlalchemy import func, select
lazy from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.models import User
from app.core.ports.datastore import DatastorePort
lazy from app.core.models.users import User as CoreUser
lazy from app.core.models.users import UserRequest


class DatastoreAdapter(DatastorePort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_user(self, user_id: UUID, user_request: UserRequest) -> CoreUser:
        user = User(id=user_id, name=user_request.name)
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user.to_core_model()

    async def get_user(self, user_id: UUID) -> CoreUser | None:
        user = await self._session.get(User, user_id)
        if user is None:
            return None
        return user.to_core_model()

    async def list_users(
        self, page_number: int, page_size: int
    ) -> tuple[list[CoreUser], int]:
        _limit = page_size
        _offset = (page_number - 1) * page_size
        _query = select(User)
        _count_query = select(func.count()).select_from(_query.subquery())
        _total = await self._session.scalar(_count_query) or 0
        _results = await self._session.scalars(
            _query.order_by(User.id).limit(_limit).offset(offset=_offset),
        )

        return [r.to_core_model() for r in _results.all()], _total

    async def update_user(self, user_id: UUID, user_request: UserRequest) -> CoreUser:
        user = await self._session.get(User, user_id)
        if user is None:
            raise ValueError(f"User with ID {user_id} not found.")
        user.name = user_request.name
        await self._session.commit()
        await self._session.refresh(user)
        return user.to_core_model()

    async def delete_user(self, user_id: UUID) -> None:
        user = await self._session.get(User, user_id)
        if user is None:
            raise ValueError(f"User with ID {user_id} not found.")
        await self._session.delete(user)
        await self._session.commit()
