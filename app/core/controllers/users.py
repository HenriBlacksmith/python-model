from uuid import UUID

from app.core.ports.datastore import DatastorePort


class UsersController:
    def __init__(self, datastore: DatastorePort):
        self._datastore = datastore

    def create_user(self, username: str) -> UUID:
        """
        Create a new user in the system.
        """
        return self._datastore.create_user(username)

    def get_user(self, user_id: UUID) -> str:
        """
        Get a user by ID.
        """
        return self._datastore.get_user(user_id)

    def update_user(self, user_id: UUID, username: str) -> None:
        """
        Update a user's username by ID.
        """
        self._datastore.update_user(user_id, username)

    def delete_user(self, user_id: UUID) -> None:
        """
        Delete a user by ID.
        """
        self._datastore.delete_user(user_id)
