from app.api.models import APIModel


class APIErrorResponse(APIModel):
    """A model representing an API error response in RFC 9457 format."""

    type: str = "about:blank"
    title: str
    detail: str | None = None
    status: int
    instance: str | None = None
