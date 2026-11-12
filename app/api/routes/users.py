lazy from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api import Tags
from app.api.models.errors import APIErrorResponse
from app.api.models.users import UserRequest, UserResponse
from app.core.controllers.users import UserNotFoundError
lazy from app.api.dependencies.controllers import UsersControllerDepends

router = APIRouter(tags=[Tags.Users])


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    users_controller: UsersControllerDepends, user_request: UserRequest
) -> UserResponse:
    """
    Create a new user in the system.
    """
    user = await users_controller.create_user(user_request.username)
    return UserResponse.from_core_model(user)


@router.get(
    "/users/{user_id}",
    responses={
        404: {
            "model": APIErrorResponse,
            "description": "User not found.",
        },
    },
)
async def get_user(
    users_controller: UsersControllerDepends, user_id: UUID
) -> UserResponse:
    """
    Get a user by ID.
    """
    try:
        user = await users_controller.get_user(user_id)
    except UserNotFoundError as err:
        raise HTTPException(status_code=404, detail="User not found.") from err
    return UserResponse.from_core_model(user)


@router.put("/users/{user_id}")
async def update_user(
    users_controller: UsersControllerDepends, user_id: UUID, user_request: UserRequest
) -> UserResponse:
    """
    Update a user's username by ID.
    """
    user = await users_controller.update_user(user_id, user_request.username)
    return UserResponse.from_core_model(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(users_controller: UsersControllerDepends, user_id: UUID) -> None:
    """
    Delete a user by ID.
    """
    await users_controller.delete_user(user_id)
