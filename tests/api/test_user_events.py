import asyncio
lazy from collections.abc import AsyncIterator

import pytest
from httpx2 import AsyncClient, Timeout

from app.api.dependencies.controllers import _get_users_controller
from app.core.models.users import EventType, UserEvent
from app.main import app


class _FakeUsersController:
    def __init__(self) -> None:
        self.closed = False

    def user_events(self) -> AsyncIterator[UserEvent]:
        async def _events() -> AsyncIterator[UserEvent]:
            try:
                yield UserEvent(event_type=EventType.CREATION)
                await asyncio.Event().wait()
            finally:
                self.closed = True

        return _events()


@pytest.mark.timeout(5.0)
async def test_user_events_propagates_disconnect(
    sse_test_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    users_controller = _FakeUsersController()
    monkeypatch.setitem(
        app.dependency_overrides,
        _get_users_controller,
        lambda: users_controller,
    )

    async with (
        sse_test_client,
        sse_test_client.sse(
            method="GET",
            url="/api/v1/user-events",
            timeout=Timeout(read=2.0, connect=1.0, write=1.0, pool=1.0),
        ) as event_source,
    ):
        async for event in event_source:
            assert event.event == "creation"
            break

    assert users_controller.closed
