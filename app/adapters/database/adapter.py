import asyncio
import json
import logging
lazy from collections.abc import AsyncGenerator
lazy from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
lazy import asyncpg
lazy from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.models import User
from app.core.errors import UsernameAlreadyInUseError, UserNotFoundError
from app.core.ports.datastore import DatastorePort
lazy from app.core.models.users import EventType, UserEvent, UserRequest
lazy from app.core.models.users import User as CoreUser

logger = logging.getLogger(__name__)


def _action_to_event_type(action: str) -> EventType:
    match action:
        case "INSERT":
            return EventType.CREATION
        case "UPDATE":
            return EventType.UPDATE
        case "DELETE":
            return EventType.DELETION
        case _:
            raise ValueError(f"Unknown action: {action}")


class DatastoreAdapter(DatastorePort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @property
    async def _asyncpg_connection(self) -> asyncpg.Connection:
        # Get asyncpg connection for gathering events
        _connection = await self._session.connection()
        _raw_connection = await _connection.get_raw_connection()
        if _raw_connection and _raw_connection.driver_connection:
            return _raw_connection.driver_connection
        raise Exception("Unable to acquire asyncpg connection")

    async def create_user(self, user_id: UUID, user_request: UserRequest) -> CoreUser:
        user = User(id=user_id, name=user_request.name)
        self._session.add(user)
        try:
            await self._session.commit()
        except IntegrityError as err:
            await self._session.rollback()
            raise UsernameAlreadyInUseError from err
        await self._session.refresh(user)
        return user.to_core_model()

    async def get_user(self, user_id: UUID) -> CoreUser:
        user = await self._session.get(User, user_id)
        if user is None:
            raise UserNotFoundError
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
            _query.order_by(User.name).limit(_limit).offset(offset=_offset),
        )

        return [r.to_core_model() for r in _results.all()], _total

    async def update_user(self, user_id: UUID, user_request: UserRequest) -> CoreUser:
        user = await self._session.get(User, user_id)
        if user is None:
            raise UserNotFoundError
        user.name = user_request.name
        try:
            await self._session.commit()
        except IntegrityError as err:
            await self._session.rollback()
            raise UsernameAlreadyInUseError from err
        await self._session.refresh(user)
        return user.to_core_model()

    async def delete_user(self, user_id: UUID) -> None:
        user = await self._session.get(User, user_id)
        if user is None:
            raise UserNotFoundError
        await self._session.delete(user)
        await self._session.commit()

    def user_events(self) -> AsyncGenerator[UserEvent]:
        async def _event_generator() -> AsyncGenerator[UserEvent]:
            queue: asyncio.Queue[UserEvent] = asyncio.Queue()

            def _callback(
                _connection: asyncpg.Connection,
                _pid: int,
                _channel: str,
                payload: str,
            ) -> None:
                try:
                    action = json.loads(payload)["action"]
                    event_type = _action_to_event_type(action)
                except (json.JSONDecodeError, KeyError, ValueError):
                    logger.warning("Dropping malformed user event payload: %s", payload)
                    return
                queue.put_nowait(UserEvent(event_type=event_type))

            connection = await self._asyncpg_connection
            channel = "user_events"
            await connection.add_listener(channel=channel, callback=_callback)
            try:
                while True:
                    yield await queue.get()
            finally:
                await connection.remove_listener(channel=channel, callback=_callback)

        return _event_generator()
