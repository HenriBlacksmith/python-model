from typing import Annotated
from uuid import UUID

from pydantic import Field

from app.api.models import APIModel


class _UserBase(APIModel):
    username: Annotated[str, Field(min_length=2, max_length=100)]


class UserRequest(_UserBase): ...


class UserResponse(_UserBase):
    user_id: UUID
