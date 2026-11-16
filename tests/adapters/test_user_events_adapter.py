import asyncio
import json
lazy from collections.abc import AsyncGenerator, Callable

import pytest

from app.adapters.database.adapter import DatastoreAdapter, _action_to_event_type
from app.core.models.users import EventType, UserEvent


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


def test_action_to_event_type_with_unknown_action() -> None:
    with pytest.raises(ValueError, match="Unknown action"):
        _action_to_event_type("TRUNCATE")


class _FakeAsyncpgConnection:
    def __init__(self) -> None:
        self.added: list[tuple[str, Callable[..., None]]] = []
        self.removed: list[tuple[str, Callable[..., None]]] = []

    async def add_listener(self, channel: str, callback: Callable[..., None]) -> None:
        self.added.append((channel, callback))

    async def remove_listener(
        self, channel: str, callback: Callable[..., None]
    ) -> None:
        self.removed.append((channel, callback))


class _FakeRawConnection:
    def __init__(self, driver_connection: _FakeAsyncpgConnection) -> None:
        self.driver_connection = driver_connection


class _FakeSQLAlchemyConnection:
    def __init__(self, raw_connection: _FakeRawConnection) -> None:
        self._raw_connection = raw_connection

    async def get_raw_connection(self) -> _FakeRawConnection:
        return self._raw_connection


class _FakeSession:
    def __init__(self, connection: _FakeSQLAlchemyConnection) -> None:
        self._connection = connection

    async def connection(self) -> _FakeSQLAlchemyConnection:
        return self._connection


def _make_adapter(connection: _FakeAsyncpgConnection) -> DatastoreAdapter:
    session = _FakeSession(_FakeSQLAlchemyConnection(_FakeRawConnection(connection)))
    return DatastoreAdapter(session=session)  # ty: ignore[invalid-argument-type]


async def _wait_for_listener(
    connection: _FakeAsyncpgConnection,
) -> tuple[str, Callable[..., None]]:
    for _ in range(1000):
        if connection.added:
            return connection.added[0]
        await asyncio.sleep(0)
    pytest.fail("Listener was never registered")


async def test_user_events_yields_events_from_notifications() -> None:
    connection = _FakeAsyncpgConnection()
    adapter = _make_adapter(connection)
    generator: AsyncGenerator[UserEvent] = adapter.user_events()
    event_task = asyncio.ensure_future(anext(generator))

    channel, callback = await _wait_for_listener(connection)
    assert channel == "user_events"

    callback(connection, 0, "user_events", json.dumps({"action": "INSERT"}))
    event = await asyncio.wait_for(event_task, timeout=1.0)
    assert event.event_type == EventType.CREATION

    await generator.aclose()
    assert connection.removed


async def test_user_events_drops_malformed_payloads() -> None:
    connection = _FakeAsyncpgConnection()
    adapter = _make_adapter(connection)
    generator: AsyncGenerator[UserEvent] = adapter.user_events()
    event_task = asyncio.ensure_future(anext(generator))

    _, callback = await _wait_for_listener(connection)
    callback(connection, 0, "user_events", "not-json")
    callback(connection, 0, "user_events", json.dumps({"data": "missing action"}))
    callback(connection, 0, "user_events", json.dumps({"action": "TRUNCATE"}))
    callback(connection, 0, "user_events", json.dumps({"action": "DELETE"}))

    event = await asyncio.wait_for(event_task, timeout=1.0)
    assert event.event_type == EventType.DELETION

    await generator.aclose()
    assert connection.removed
