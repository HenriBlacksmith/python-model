from uuid import uuid4
lazy from collections.abc import AsyncGenerator, AsyncIterable

from fastapi import APIRouter
from fastapi.sse import EventSourceResponse, ServerSentEvent

from app.api import Tags
from app.api.dependencies.controllers import UsersControllerDepends
from app.core.models.users import UserEvent

router = APIRouter(tags=[Tags.UserEvents])


@router.get("/user-events", response_class=EventSourceResponse)
async def get_user_events(
    users_controller: UsersControllerDepends,
) -> AsyncIterable[ServerSentEvent]:
    event_generator: AsyncGenerator[UserEvent] = users_controller.user_events()
    try:
        async for event in event_generator:
            yield ServerSentEvent(
                data=event.event_type, event=event.event_type, id=str(uuid4())
            )
    finally:
        await event_generator.aclose()
