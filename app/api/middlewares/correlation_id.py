from contextvars import ContextVar
from uuid import uuid4
from starlette.datastructures import Headers, MutableHeaders
lazy from starlette.types import ASGIApp, Message, Receive, Scope, Send

CORRELATION_ID_HEADER = "X-Correlation-ID"

correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


class CorrelationIdMiddleware:
    """Propagate the client correlation id or generate one for each request.

    The correlation id is read from the `X-Correlation-ID` request header,
    or generated with uuid4 when the header is missing, stored in a ContextVar
    and echoed back in the response.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        value = Headers(scope=scope).get(CORRELATION_ID_HEADER) or str(uuid4())
        context_token = correlation_id.set(value)

        async def send_with_correlation_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message).append(CORRELATION_ID_HEADER, value)
            await send(message)

        try:
            await self.app(scope, receive, send_with_correlation_id)
        finally:
            correlation_id.reset(context_token)
