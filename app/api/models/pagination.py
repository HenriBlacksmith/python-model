from typing import Annotated, Self

from annotated_types import Ge, Gt
from pydantic import BaseModel
lazy from pydantic import HttpUrl

from app.api.models import APIModel
from app.core.config import settings


class PaginationQueryParameters(BaseModel):
    page_size: Annotated[int, Gt(gt=0)] = settings.api.default_page_size
    page: Annotated[int, Gt(gt=0)]


class PaginationLinks(APIModel):
    self: HttpUrl
    first: HttpUrl
    last: HttpUrl
    prev: HttpUrl | None
    next: HttpUrl | None

    @classmethod
    def build(cls, path: str, page_size: int, page: int, total: int) -> PaginationLinks:
        last_page = total // page_size + 1
        return cls(
            self=HttpUrl(
                f"{settings.api.base_url}{path}?page={page}&page_size={page_size}"
            ),
            first=HttpUrl(
                f"{settings.api.base_url}{path}?page=1&page_size={page_size}"
            ),
            last=HttpUrl(
                f"{settings.api.base_url}{path}?page={last_page}&page_size={page_size}"
            ),
            prev=None
            if page == 1
            else HttpUrl(
                f"{settings.api.base_url}{path}?page={page - 1}&page_size={page_size}"
            ),
            next=None
            if page == last_page
            else HttpUrl(
                f"{settings.api.base_url}{path}?page={page + 1}&page_size={page_size}"
            ),
        )


class PaginatedResponse[T: APIModel](APIModel):
    page_size: Annotated[int, Gt(gt=0)]
    page: Annotated[int, Gt(gt=0)]
    total: Annotated[int, Ge(ge=0)]
    data: list[T]
    links: PaginationLinks

    @classmethod
    def build(
        cls, data: list[T], path: str, page_size: int, page: int, total: int
    ) -> Self:
        return cls(
            page_size=page_size,
            page=page,
            total=total,
            data=data,
            links=PaginationLinks.build(path, page_size, page, total),
        )
