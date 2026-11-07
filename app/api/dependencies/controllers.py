from typing import Annotated

from fastapi import Depends

from app.api.dependencies.database import DatabaseAdapterDepends
from app.core.controllers.users import UsersController


def _get_users_controller(datastore: DatabaseAdapterDepends) -> UsersController:
    return UsersController(datastore=datastore)


UsersControllerDepends = Annotated[UsersController, Depends(_get_users_controller)]
