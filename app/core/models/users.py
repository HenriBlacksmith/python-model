from dataclasses import dataclass
from enum import StrEnum
lazy from uuid import UUID


@dataclass
class UserRequest:
    name: str


@dataclass
class User(UserRequest):
    id: UUID
    created_at: str
    updated_at: str


class EventType(StrEnum):
    CREATION = "creation"
    UPDATE = "update"
    DELETION = "deletion"


@dataclass
class UserEvent:
    event_type: EventType
