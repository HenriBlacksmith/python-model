lazy from uuid import UUID

lazy from sqlalchemy.orm import Session

from app.adapters.database.models import User
from app.core.ports.datastore import DatastorePort
lazy from app.core.models.users import User as CoreUser
lazy from app.core.models.users import UserRequest


class DatastoreAdapter(DatastorePort):
    def __init__(self, session: Session) -> None:
        self._session = session

    async def create_user(self, user_id: UUID, user_request: UserRequest) -> CoreUser:
        user = User(id=user_id, name=user_request.name)
        self._session.add(user)
        self._session.commit()
        return user.to_core_model()

    async def get_user(self, user_id: UUID) -> CoreUser:
        user = self._session.get(User, user_id)
        if user is None:
            raise ValueError(f"User with ID {user_id} not found.")
        return user.to_core_model()

    async def update_user(self, user_id: UUID, user_request: UserRequest) -> CoreUser:
        user = self._session.get(User, user_id)
        if user is None:
            raise ValueError(f"User with ID {user_id} not found.")
        user.name = user_request.name
        self._session.commit()
        self._session.refresh(user)
        return user.to_core_model()

    async def delete_user(self, user_id: UUID) -> None:
        user = self._session.get(User, user_id)
        if user is None:
            raise ValueError(f"User with ID {user_id} not found.")
        self._session.delete(user)
        self._session.commit()
