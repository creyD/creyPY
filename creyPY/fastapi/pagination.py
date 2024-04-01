from math import ceil
from typing import Any, Generic, Optional, Self, Sequence, TypeVar

from fastapi_pagination import Params
from fastapi_pagination.bases import AbstractPage, AbstractParams
from fastapi_pagination.types import GreaterEqualOne, GreaterEqualZero
from pydantic.json_schema import SkipJsonSchema

T = TypeVar("T")


# SkipJsonSchema is used to avoid generating invalid JSON schema in FastAPI
class Page(AbstractPage[T], Generic[T]):
    results: Sequence[T]
    page: GreaterEqualOne | SkipJsonSchema[None] = None
    size: GreaterEqualOne | SkipJsonSchema[None] = None
    pages: GreaterEqualZero | SkipJsonSchema[None] = None
    total: GreaterEqualZero
    has_next: bool | SkipJsonSchema[None] = None
    has_prev: bool | SkipJsonSchema[None] = None

    __params_type__ = Params

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        params: AbstractParams,
        *,
        total: Optional[int] = None,
        **kwargs: Any,
    ) -> Self:
        if not isinstance(params, Params):
            raise TypeError("Page should be used with Params")

        size = params.size or total or len(items)
        page = params.page or 1
        pages = None

        if total is not None:
            if total == 0:
                pages = 1
            else:
                pages = ceil(total / size)

        has_next = page < (pages or 1)
        has_prev = page > 1

        return cls(
            total=total,
            results=items,
            page=page,
            size=size,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev,
        )


# Parse response from an SDK to a PAGE
def parse_page(response, page: int, size: int) -> Page:
    return Page(
        page=page,
        size=size,
        total=response.total,
        results=response.results,
        pages=response.pages or 1,
        has_next=response.has_next,
        has_prev=response.has_prev,
    )
