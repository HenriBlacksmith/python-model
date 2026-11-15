import asyncio
from contextlib import suppress
from uuid import uuid4
lazy from collections.abc import AsyncGenerator, AsyncIterable

from fastapi import APIRouter, Request
from fastapi.sse import EventSourceResponse, ServerSentEvent

from app.api import Tags
from app.api.dependencies.controllers import UsersControllerDepends
from app.core.models.users import UserEvent

router = APIRouter(tags=[Tags.UserEvents])


async def _watch_disconnect(request: Request, disconnected: asyncio.Event) -> None:
    while True:
        message = await request.receive()
        if message["type"] == "http.disconnect":
            disconnected.set()
            return


@router.get("/user-events", response_class=EventSourceResponse)
async def get_user_events(
    request: Request,
    users_controller: UsersControllerDepends,
) -> AsyncIterable[ServerSentEvent]:
    disconnected = asyncio.Event()
    event_generator: AsyncGenerator[UserEvent] | None = None
    disconnect_watcher = asyncio.create_task(_watch_disconnect(request, disconnected))
    try:
        event_generator = await users_controller.user_events(disconnected)
        async for event in event_generator:
            yield ServerSentEvent(
                data=event.event_type, event=event.event_type, id=str(uuid4())
            )
    finally:
        disconnected.set()
        disconnect_watcher.cancel()
        with suppress(asyncio.CancelledError):
            await disconnect_watcher
        if event_generator is not None:
            await event_generator.aclose()
