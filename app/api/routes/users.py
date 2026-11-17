from typing import Annotated
lazy from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api import Tags
from app.api.models.errors import (
    APIErrorResponse,
    APIUnhandledErrorResponse,
    APIValidationErrorResponse,
)
from app.api.models.pagination import (
    PaginatedResponse,
    PaginationQueryParameters,
)
from app.api.models.users import UserRequest, UserResponse
from app.core.errors import UsernameAlreadyInUseError, UserNotFoundError
lazy from app.api.dependencies.auth import require_scopes
lazy from app.api.dependencies.controllers import UsersControllerDepends

router = APIRouter(tags=[Tags.Users])

_VALIDATION_ERROR_RESPONSE = {
    "content": {
        "application/problem+json": {
            "schema": APIValidationErrorResponse.model_json_schema(),
        },
    },
    "description": "The request was invalid.",
}

_NOT_FOUND_RESPONSE = {
    "content": {
        "application/problem+json": {
            "schema": APIErrorResponse.model_json_schema(),
        },
    },
    "description": "User not found.",
}

_CONFLICT_RESPONSE = {
    "content": {
        "application/problem+json": {
            "schema": APIErrorResponse.model_json_schema(),
        },
    },
    "description": "The requested username is already in use.",
}

_UNHANDLED_ERROR_RESPONSE = {
    "content": {
        "application/problem+json": {
            "schema": APIUnhandledErrorResponse.model_json_schema(),
        },
    },
    "description": "An unexpected error occurred.",
}

_UNAUTHORIZED_RESPONSE = {
    "content": {
        "application/problem+json": {
            "schema": APIErrorResponse.model_json_schema(),
        },
    },
    "description": "Missing or invalid authentication token.",
}

_FORBIDDEN_RESPONSE = {
    "content": {
        "application/problem+json": {
            "schema": APIErrorResponse.model_json_schema(),
        },
    },
    "description": "The access token does not have the required scopes.",
}


@router.post(
    "/users",
    dependencies=[Depends(require_scopes("users:write"))],
    status_code=status.HTTP_201_CREATED,
    responses={
        401: _UNAUTHORIZED_RESPONSE,
        403: _FORBIDDEN_RESPONSE,
        400: _VALIDATION_ERROR_RESPONSE,
        500: _UNHANDLED_ERROR_RESPONSE,
    },
)
async def create_user(
    users_controller: UsersControllerDepends, user_request: UserRequest
) -> UserResponse:
    """
    Create a new user in the system.
    """
    try:
        user = await users_controller.create_user(user_request.username)
    except UsernameAlreadyInUseError as err:
        raise HTTPException(status_code=409, detail=err.message) from err
    return UserResponse.from_core_model(user)


@router.get(
    "/users/{user_id}",
    dependencies=[Depends(require_scopes("users:read"))],
    responses={
        401: _UNAUTHORIZED_RESPONSE,
        403: _FORBIDDEN_RESPONSE,
        404: _NOT_FOUND_RESPONSE,
        409: _CONFLICT_RESPONSE,
        500: _UNHANDLED_ERROR_RESPONSE,
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
        return UserResponse.from_core_model(user)
    except UserNotFoundError as err:
        raise HTTPException(status_code=404, detail=err.message) from err


@router.get(
    "/users",
    dependencies=[Depends(require_scopes("users:read"))],
    responses={
        401: _UNAUTHORIZED_RESPONSE,
        403: _FORBIDDEN_RESPONSE,
        500: _UNHANDLED_ERROR_RESPONSE,
    },
)
async def list_users(
    users_controller: UsersControllerDepends,
    pagination_query: Annotated[PaginationQueryParameters, Query()],
) -> PaginatedResponse[UserResponse]:
    users, total = await users_controller.list_users(
        pagination_query.page, pagination_query.page_size
    )
    return PaginatedResponse.build(
        path="api/v1/users",
        page_size=pagination_query.page_size,
        page=pagination_query.page,
        total=total,
        data=[UserResponse.from_core_model(user) for user in users],
    )


@router.put(
    "/users/{user_id}",
    dependencies=[Depends(require_scopes("users:write"))],
    responses={
        401: _UNAUTHORIZED_RESPONSE,
        403: _FORBIDDEN_RESPONSE,
        404: _NOT_FOUND_RESPONSE,
        409: _CONFLICT_RESPONSE,
        500: _UNHANDLED_ERROR_RESPONSE,
    },
)
async def update_user(
    users_controller: UsersControllerDepends, user_id: UUID, user_request: UserRequest
) -> UserResponse:
    """
    Update a user's username by ID.
    """
    try:
        user = await users_controller.update_user(user_id, user_request.username)
        return UserResponse.from_core_model(user)
    except UserNotFoundError as err:
        raise HTTPException(status_code=404, detail=err.message) from err
    except UsernameAlreadyInUseError as err:
        raise HTTPException(status_code=409, detail=err.message) from err


@router.delete(
    "/users/{user_id}",
    dependencies=[Depends(require_scopes("users:write"))],
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    responses={
        401: _UNAUTHORIZED_RESPONSE,
        403: _FORBIDDEN_RESPONSE,
        404: _NOT_FOUND_RESPONSE,
        500: _UNHANDLED_ERROR_RESPONSE,
    },
)
async def delete_user(users_controller: UsersControllerDepends, user_id: UUID) -> None:
    """
    Delete a user by ID.
    """
    try:
        await users_controller.delete_user(user_id)
    except UserNotFoundError as err:
        raise HTTPException(status_code=404, detail=err.message) from err
