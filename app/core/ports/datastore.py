from abc import ABC, abstractmethod
from uuid import UUID


class DatastorePort(ABC):
    @abstractmethod
    def create_user(self, username: str) -> UUID: ...

    @abstractmethod
    def get_user(self, user_id: UUID) -> str: ...

    @abstractmethod
    def update_user(self, user_id: UUID, username: str) -> None: ...

    @abstractmethod
    def delete_user(self, user_id: UUID) -> None: ...
