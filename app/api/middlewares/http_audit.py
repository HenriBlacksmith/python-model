import contextlib
import logging
import time
from typing import Any
lazy from collections.abc import Awaitable, Callable
lazy from starlette.types import ASGIApp, Message, Receive, Scope, Send

import jwt
from starlette.datastructures import Headers

from app.adapters.configuration.settings import settings
from app.adapters.logging.audit import AUDIT_LOGGER_NAME
from app.api.middlewares.correlation_id import CORRELATION_ID_HEADER

audit_logger = logging.getLogger(name=AUDIT_LOGGER_NAME)


class HttpAuditLogMiddleware:
    """Emit one structured audit log record per audited HTTP request."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not self._is_audited(path=scope["path"]):
            await self.app(scope=scope, receive=receive, send=send)
            return

        start = time.perf_counter()
        status_code = 500
        error_type: str | None = None
        error_message: str | None = None

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope=scope, receive=receive, send=send_wrapper)
        except Exception as exc:
            error_type = type(exc).__name__
            error_message = str(exc)
            raise
        finally:
            self._log_audit(
                scope=scope,
                status_code=status_code,
                duration_ms=int((time.perf_counter() - start) * 1000),
                error_type=error_type,
                error_message=error_message,
            )

    def _is_audited(self, path: str) -> bool:
        audit = settings.audit
        if not audit.enabled:
            return False
        return not any(
            path.startswith(excluded) for excluded in audit.exclude_paths
        )

    @staticmethod
    def _user_id(headers: Headers) -> str | None:
        """Extract the JWT subject without verifying the signature.

        The middleware runs before authentication, so the token can only be
        decoded permissively; the verified subject is enforced later by the
        auth dependency.
        """
        token: str = headers.get("authorization", "").removeprefix("Bearer ").strip()
        if not token:
            return None
        with contextlib.suppress(jwt.PyJWTError):
            claims = jwt.decode(
                jwt=token,
                options={"verify_signature": False},
            )
            subject: str | None = claims.get("sub")
            return subject
        return None

    def _log_audit(
        self,
        scope: Scope,
        status_code: int,
        duration_ms: int,
        error_type: str | None,
        error_message: str | None,
    ) -> None:
        headers = Headers(scope=scope)
        client = scope.get("client")
        query: str = scope.get("query_string", b"").decode(errors="replace")
        forwarded_for: str = headers.get("x-forwarded-for", "")
        client_ip: str | None = (
            forwarded_for.split(",")[0].strip() or client[0] if client else None
        )
        details: dict[str, Any] = {
            "http_request_method": scope["method"],
            "http_request_id": headers.get(CORRELATION_ID_HEADER),
            "http_response_status_code": status_code,
            "url_path": scope["path"],
            "client_address": client_ip,
            "client_port": client[1] if client else None,
            "user_id": self._user_id(headers=headers),
            "user_agent_original": headers.get("user-agent"),
            "duration_ms": duration_ms,
            "error_type": error_type,
            "error_message": error_message,
        }
        if query:
            details["url_query"] = query
        message = f'{details["http_request_method"]} {scope["path"]} {status_code}'
        audit_logger.info(msg=message, extra=details)
