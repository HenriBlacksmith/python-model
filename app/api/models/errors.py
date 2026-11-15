from fastapi.responses import JSONResponse

from app.api.models import APIModel


class ProblemJSONResponse(JSONResponse):
    media_type = "application/problem+json"


class APIErrorResponse(APIModel):
    """A model representing an API error response in RFC 9457 format."""

    type: str = "about:blank"
    title: str
    detail: str | None = None
    status: int
    instance: str | None = None


class APIValidationError(APIModel):
    detail: str
    pointer: str


class APIValidationErrorResponse(APIErrorResponse):
    errors: list[APIValidationError]
