from typing import Annotated

from annotated_types import Gt
from pydantic import BaseModel
lazy from pydantic import HttpUrl

from app.api.models import APIModel


class PaginationQueryParameters(BaseModel):
    page_size: Annotated[int, Gt(gt=0)]
    page: Annotated[int, Gt(gt=0)]


class PaginationLinks(APIModel):
    self: HttpUrl
    first: HttpUrl
    last: HttpUrl
    prev: HttpUrl
    next: HttpUrl


class PaginatedResponse[T: APIModel](APIModel):
    page_size: Annotated[int, Gt(gt=0)]
    page: Annotated[int, Gt(gt=0)]
    total: Annotated[int, Gt(gt=0)]
    data: list[T]
    links: PaginationLinks
