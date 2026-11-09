from uuid import UUID, uuid4

from app.core.models.users import User, UserRequest
from app.core.ports.datastore import DatastorePort


class UsersController:
    def __init__(self, datastore: DatastorePort):
        self._datastore = datastore

    def create_user(self, username: str) -> User:
        """
        Create a new user in the system.
        """
        user_request = UserRequest(name=username)
        user_id = uuid4()
        return self._datastore.create_user(user_id, user_request)

    def get_user(self, user_id: UUID) -> User:
        """
        Get a user by ID.
        """
        return self._datastore.get_user(user_id)

    def update_user(self, user_id: UUID, username: str) -> User:
        """
        Update a user's username by ID.
        """
        user_request = UserRequest(name=username)
        return self._datastore.update_user(user_id, user_request)

    def delete_user(self, user_id: UUID) -> None:
        """
        Delete a user by ID.
        """
        self._datastore.delete_user(user_id)
