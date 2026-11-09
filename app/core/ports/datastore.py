from abc import ABC, abstractmethod
from uuid import UUID

from app.core.models.users import User, UserRequest


class DatastorePort(ABC):
    @abstractmethod
    def create_user(self, user_id: UUID, user_request: UserRequest) -> User: ...

    @abstractmethod
    def get_user(self, user_id: UUID) -> User: ...

    @abstractmethod
    def update_user(self, user_id: UUID, user_request: UserRequest) -> None: ...

    @abstractmethod
    def delete_user(self, user_id: UUID) -> None: ...
