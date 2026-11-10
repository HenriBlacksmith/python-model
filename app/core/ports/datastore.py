from abc import ABC, abstractmethod
lazy from uuid import UUID

from app.core.models.users import User, UserRequest


class DatastorePort(ABC):
    @abstractmethod
    async def create_user(self, user_id: UUID, user_request: UserRequest) -> User: ...

    @abstractmethod
    async def get_user(self, user_id: UUID) -> User: ...

    @abstractmethod
    async def update_user(self, user_id: UUID, user_request: UserRequest) -> User: ...

    @abstractmethod
    async def delete_user(self, user_id: UUID) -> None: ...
