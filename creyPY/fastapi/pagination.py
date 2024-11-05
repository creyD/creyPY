from math import ceil
from typing import Any, Generic, Optional, Self, Sequence, TypeVar, Union
from pydantic import BaseModel
from fastapi_pagination import Params
from fastapi_pagination.bases import AbstractPage, AbstractParams
from fastapi_pagination.types import (
    GreaterEqualOne,
    GreaterEqualZero,
    AdditionalData,
    SyncItemsTransformer,
)
from fastapi_pagination.api import create_page, apply_items_transformer
from fastapi_pagination.utils import verify_params
from fastapi_pagination.ext.sqlalchemy import create_paginate_query
from fastapi_pagination.bases import AbstractParams, RawParams
from pydantic.json_schema import SkipJsonSchema
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm.session import Session
from sqlalchemy import select, func
from fastapi import Query

T = TypeVar("T")


class PaginationParams(BaseModel, AbstractParams):
    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(50, ge=1, le=100, description="Page size")
    pagination: bool = Query(True, description="Toggle pagination")

    def to_raw_params(self) -> RawParams:
        if not self.pagination:
            return RawParams(limit=None, offset=None)

        return RawParams(limit=self.size, offset=(self.page - 1) * self.size)


# TODO: Add complete fastapi-pagination proxy here
# TODO: Add pagination off functionality
# SkipJsonSchema is used to avoid generating invalid JSON schema in FastAPI
class Page(AbstractPage[T], Generic[T]):
    results: Sequence[T]
    page: GreaterEqualOne | SkipJsonSchema[None] = None
    size: GreaterEqualOne | SkipJsonSchema[None] = None
    pages: GreaterEqualZero | SkipJsonSchema[None] = None
    total: GreaterEqualZero
    has_next: bool | SkipJsonSchema[None] = None
    has_prev: bool | SkipJsonSchema[None] = None

    __params_type__ = PaginationParams

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


def create_count_query(query: Select) -> Select:
    return select(func.count()).select_from(query.subquery())


def unwrap_scalars(
    items: Sequence[Sequence[T]],
    force_unwrap: bool = True,
) -> Union[Sequence[T], Sequence[Sequence[T]]]:
    return [item[0] if force_unwrap else item for item in items]


def paginate(
    connection: Session,
    query: Select,
    params: Optional[AbstractParams] = None,
    transformer: Optional[SyncItemsTransformer] = None,
    additional_data: Optional[AdditionalData] = None,
):

    params, raw_params = verify_params(params, "limit-offset", "cursor")
    count_query = create_count_query(query)
    total = connection.scalar(count_query)

    if params.pagination is False and total > 0:
        params = Params(page=1, size=total)
    else:
        params = Params(page=params.page, size=params.size)

    query = create_paginate_query(query, params)
    items = connection.execute(query).all()

    items = unwrap_scalars(items)
    t_items = apply_items_transformer(items, transformer)

    return create_page(
        t_items,
        params=params,
        total=total,
        **(additional_data or {}),
    )
