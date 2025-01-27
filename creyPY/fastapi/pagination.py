from contextlib import suppress
from math import ceil
from typing import Any, Generic, Optional, Self, Sequence, TypeVar, Union, overload

from fastapi import Query
from fastapi_pagination.api import apply_items_transformer, create_page
from fastapi_pagination.bases import AbstractPage, AbstractParams, RawParams
from fastapi_pagination.ext.sqlalchemy import create_paginate_query
from fastapi_pagination.types import (
    AdditionalData,
    AsyncItemsTransformer,
    GreaterEqualOne,
    GreaterEqualZero,
    ItemsTransformer,
    SyncItemsTransformer,
)
from fastapi_pagination.utils import verify_params
from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.selectable import Select
from sqlalchemy.util import await_only, greenlet_spawn

T = TypeVar("T")


class PaginationParams(BaseModel, AbstractParams):
    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(50, ge=1, description="Page size")
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
        if not isinstance(params, PaginationParams):
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


def _get_sync_conn_from_async(conn: Any) -> Session:  # pragma: no cover
    if isinstance(conn, async_scoped_session):
        conn = conn()

    with suppress(AttributeError):
        return conn.sync_session  # type: ignore

    with suppress(AttributeError):
        return conn.sync_connection  # type: ignore

    raise TypeError("conn must be an AsyncConnection or AsyncSession")


@overload
def paginate(
    connection: Session,
    query: Select,
    params: Optional[AbstractParams] = None,
    transformer: Optional[SyncItemsTransformer] = None,
    additional_data: Optional[AdditionalData] = None,
) -> Any:
    pass


@overload
async def paginate(
    connection: AsyncSession,
    query: Select,
    params: Optional[AbstractParams] = None,
    transformer: Optional[AsyncItemsTransformer] = None,
    additional_data: Optional[AdditionalData] = None,
) -> Any:
    pass


def _paginate(
    connection: Session,
    query: Select,
    params: Optional[AbstractParams] = None,
    transformer: Optional[ItemsTransformer] = None,
    additional_data: Optional[AdditionalData] = None,
    async_: bool = False,
):

    if async_:

        def _apply_items_transformer(*args: Any, **kwargs: Any) -> Any:
            return await_only(apply_items_transformer(*args, **kwargs, async_=True))

    else:
        _apply_items_transformer = apply_items_transformer

    params, raw_params = verify_params(params, "limit-offset", "cursor")
    count_query = create_count_query(query)
    total = connection.scalar(count_query)

    if params.pagination is False and total > 0:
        params = PaginationParams(page=1, size=total)
    else:
        params = PaginationParams(page=params.page, size=params.size)

    query = create_paginate_query(query, params)
    items = connection.execute(query).all()

    items = unwrap_scalars(items)
    t_items = _apply_items_transformer(items, transformer)

    return create_page(
        t_items,
        params=params,
        total=total,
        **(additional_data or {}),
    )


def paginate(
    connection: Session,
    query: Select,
    params: Optional[AbstractParams] = None,
    transformer: Optional[ItemsTransformer] = None,
    additional_data: Optional[AdditionalData] = None,
):
    if isinstance(connection, AsyncSession):
        connection = _get_sync_conn_from_async(connection)
        return greenlet_spawn(
            _paginate, connection, query, params, transformer, additional_data, async_=True
        )

    return _paginate(connection, query, params, transformer, additional_data, async_=False)
