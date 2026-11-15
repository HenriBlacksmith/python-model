from uuid import uuid4
lazy from collections.abc import AsyncIterable

from fastapi import APIRouter
from fastapi.sse import EventSourceResponse, ServerSentEvent

from app.api import Tags
from app.api.models.events import UserEvent

router = APIRouter(tags=[Tags.UserEvents])

events = [UserEvent(event="creation")]


@router.get("/users/events", response_class=EventSourceResponse)
async def get_user_events() -> AsyncIterable[ServerSentEvent]:
    for event in events:
        yield ServerSentEvent(data="", event=event.event, id=str(uuid4()))
