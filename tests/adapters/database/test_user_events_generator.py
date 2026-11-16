import asyncio
import json
from typing import Any, cast
from unittest.mock import MagicMock
lazy from collections.abc import Callable

import pytest
lazy from pytest_mock import MockerFixture
lazy from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.adapter import DatastoreAdapter, _action_to_event_type
from app.core.models.users import EventType, UserEvent

UserEventCallback = Callable[[Any, int, str, str], None]


class _FakeAsyncpgConnection:
    def __init__(self) -> None:
        self.callback: UserEventCallback | None = None
        self.listener_removed = False
        self.registered = asyncio.Event()

    async def add_listener(self, channel: str, callback: UserEventCallback) -> None:
        self.channel = channel
        self.callback = callback
        self.registered.set()

    async def remove_listener(self, channel: str, callback: UserEventCallback) -> None:
        self.channel = channel
        self.listener_removed = callback is self.callback

    def notify(self, payload: str) -> None:
        if self.callback is None:
            raise AssertionError("listener not registered")
        self.callback(None, 0, self.channel, payload)


@pytest.mark.parametrize(
    ("action", "expected_event_type"),
    [
        ("INSERT", EventType.CREATION),
        ("UPDATE", EventType.UPDATE),
        ("DELETE", EventType.DELETION),
    ],
)
def test_action_to_event_type(action: str, expected_event_type: EventType) -> None:
    assert _action_to_event_type(action) == expected_event_type


@pytest.mark.parametrize("action", ["TRUNCATE", ""])
def test_action_to_event_type_with_unknown_action(action: str) -> None:
    with pytest.raises(ValueError, match="Unknown action"):
        _action_to_event_type(action)


def _make_adapter(
    fake_connection: _FakeAsyncpgConnection, mocker: MockerFixture
) -> DatastoreAdapter:
    async def _fake_connection(_self: DatastoreAdapter) -> _FakeAsyncpgConnection:
        return fake_connection

    mocker.patch.object(
        DatastoreAdapter,
        "_asyncpg_connection",
        property(_fake_connection),
    )
    return DatastoreAdapter(session=cast("AsyncSession", MagicMock()))


@pytest.mark.timeout(5.0)
async def test_user_events_generator_yields_events_in_order(
    mocker: MockerFixture,
) -> None:
    fake_connection = _FakeAsyncpgConnection()
    adapter = _make_adapter(fake_connection, mocker)
    generator = adapter.user_events()

    first_task = asyncio.create_task(anext(generator))
    await fake_connection.registered.wait()
    fake_connection.notify(json.dumps({"action": "INSERT"}))
    fake_connection.notify(json.dumps({"action": "UPDATE"}))

    first_event = await asyncio.wait_for(first_task, timeout=1.0)
    second_event = await asyncio.wait_for(anext(generator), timeout=1.0)

    assert first_event == UserEvent(event_type=EventType.CREATION)
    assert second_event == UserEvent(event_type=EventType.UPDATE)

    await generator.aclose()
    assert fake_connection.listener_removed


@pytest.mark.timeout(5.0)
async def test_user_events_generator_drops_malformed_payloads(
    mocker: MockerFixture,
) -> None:
    fake_connection = _FakeAsyncpgConnection()
    adapter = _make_adapter(fake_connection, mocker)
    logger_mock = mocker.patch("app.adapters.database.adapter.logger")
    generator = adapter.user_events()

    first_task = asyncio.create_task(anext(generator))
    await fake_connection.registered.wait()
    fake_connection.notify("not-json")
    fake_connection.notify(json.dumps({"nope": 1}))
    fake_connection.notify(json.dumps({"action": "TRUNCATE"}))
    fake_connection.notify(json.dumps({"action": "DELETE"}))

    event = await asyncio.wait_for(first_task, timeout=1.0)

    assert event == UserEvent(event_type=EventType.DELETION)
    assert logger_mock.warning.call_count == 3

    await generator.aclose()
    assert fake_connection.listener_removed
