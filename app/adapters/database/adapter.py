from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.adapters.database.models import User
from app.core.ports.datastore import DatastorePort


class DatastoreAdapter(DatastorePort):
    def __init__(self, session: Session):
        self._session = session

    def create_user(self, username: str) -> UUID:
        user_id = uuid4()
        self._session.add(User(id=user_id, name=username))
        self._session.commit()
        return user_id

    def get_user(self, user_id: UUID) -> str:
        user = self._session.get(User, user_id)
        if user is None:
            raise ValueError(f"User with ID {user_id} not found.")
        return user.name

    def update_user(self, user_id: UUID, username: str) -> None:
        user = self._session.get(User, user_id)
        if user is None:
            raise ValueError(f"User with ID {user_id} not found.")
        user.name = username
        self._session.commit()

    def delete_user(self, user_id: UUID) -> None:
        user = self._session.get(User, user_id)
        if user is None:
            raise ValueError(f"User with ID {user_id} not found.")
        self._session.delete(user)
        self._session.commit()
