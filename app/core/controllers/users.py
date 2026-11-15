from uuid import UUID, uuid4
lazy from asyncio import Event
lazy from collections.abc import AsyncGenerator

from app.core.models.users import User, UserEvent, UserRequest
lazy from app.core.ports.datastore import DatastorePort


class UsersController:
    def __init__(self, datastore: DatastorePort) -> None:
        self._datastore = datastore

    async def create_user(self, username: str) -> User:
        """
        Create a new user in the system.
        """
        user_request = UserRequest(name=username)
        user_id = uuid4()
        return await self._datastore.create_user(user_id, user_request)

    async def get_user(self, user_id: UUID) -> User:
        """
        Get a user by ID.
        """
        return await self._datastore.get_user(user_id)

    async def list_users(
        self, page_number: int, page_size: int
    ) -> tuple[list[User], int]:
        """
        Get a page of users.
        """
        return await self._datastore.list_users(page_number, page_size)

    async def update_user(self, user_id: UUID, username: str) -> User:
        """
        Update a user's username by ID.
        """
        user_request = UserRequest(name=username)
        return await self._datastore.update_user(user_id, user_request)

    async def delete_user(self, user_id: UUID) -> None:
        """
        Delete a user by ID.
        """
        await self._datastore.delete_user(user_id)

    async def user_events(self, disconnected: Event) -> AsyncGenerator[UserEvent]:
        """
        Stream user events.
        """
        return self._datastore.user_events(disconnected)
