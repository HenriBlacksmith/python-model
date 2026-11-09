from dataclasses import dataclass
from uuid import UUID


@dataclass
class UserRequest:
    name: str


@dataclass
class User(UserRequest):
    id: UUID
    created_at: str
    updated_at: str
