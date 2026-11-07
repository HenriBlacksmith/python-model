from uuid import UUID

from pydantic import BaseModel


class UserRequest(BaseModel):
    username: str


class UserResponse(BaseModel):
    user_id: UUID
    username: str
