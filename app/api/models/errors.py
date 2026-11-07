from app.api.models import APIModel


class APIErrorResponse(APIModel):
    """A model representing an API error response."""

    message: str
    code: str
