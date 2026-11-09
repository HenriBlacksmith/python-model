from typing import Annotated
lazy from datetime import datetime
lazy from uuid import UUID

from pydantic import Field

from app.api.models import APIModel
lazy from app.core.models.users import User


class _UserBase(APIModel):
    username: Annotated[str, Field(min_length=2, max_length=100)]


class UserRequest(_UserBase): ...


class UserResponse(_UserBase):
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_core_model(cls, user: User) -> UserResponse:
        return cls(
            user_id=user.id,
            username=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
