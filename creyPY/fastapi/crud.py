import asyncio
from typing import List, Type, TypeVar, overload
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from .models.base import Base

T = TypeVar("T", bound=Base)


@overload
async def get_object_or_404(
    db_class: Type[T],
    id: UUID | str,
    db: AsyncSession,
    expunge: bool = False,
    lookup_column: str = "id",
    response_fields: List[str] = [],
) -> T:
    pass


@overload
def get_object_or_404(
    db_class: Type[T],
    id: UUID | str,
    db: Session,
    expunge: bool = False,
    lookup_column: str = "id",
    response_fields: List[str] = [],
) -> T:
    pass


def get_object_or_404(
    db_class: Type[T],
    id: UUID | str,
    db: Session | AsyncSession,
    expunge: bool = False,
    lookup_column: str = "id",
    response_fields: List[str] = [],
) -> T:

    async def _get_async_object() -> T:
        if response_fields:
            selected_columns = [
                getattr(db_class, field) for field in response_fields if hasattr(db_class, field)
            ]
            query = select(*selected_columns).where(getattr(db_class, lookup_column) == id)
            result = await db.execute(query)
            row = result.first()

            if row is None:
                raise HTTPException(status_code=404, detail="The object does not exist.")
            if hasattr(row, "_mapping"):
                obj_dict = dict(row._mapping)
            else:
                obj_dict = {column.key: getattr(row, column.key) for column in selected_columns}
        else:
            query = select(db_class).where(getattr(db_class, lookup_column) == id)
            result = await db.execute(query)
            row = result.scalar_one_or_none()
            if row is None:
                raise HTTPException(status_code=404, detail="The object does not exist.")
            obj_dict = row
        if expunge:
            await db.expunge(obj_dict)
        return obj_dict

    def _get_sync_object() -> T:
        if response_fields:
            selected_columns = [
                getattr(db_class, field) for field in response_fields if hasattr(db_class, field)
            ]
            query = db.query(*selected_columns).filter(getattr(db_class, lookup_column) == id)
        else:
            query = db.query(db_class).filter(getattr(db_class, lookup_column) == id)
        obj = query.one_or_none()
        if obj is None:
            raise HTTPException(status_code=404, detail="The object does not exist.")  # type: ignore
        if expunge:
            db.expunge(obj)
        return obj

    if isinstance(db, AsyncSession):
        return asyncio.ensure_future(_get_async_object())  # type: ignore
    elif isinstance(db, Session):
        return _get_sync_object()
    else:
        raise HTTPException(status_code=404, detail="Invalid session type. Expected Session or AsyncSession.")  # type: ignore


# TODO: Add testing
@overload
async def create_obj_from_data(
    data: BaseModel,
    model: Type[T],
    db: AsyncSession,
    additional_data: dict = {},
    exclude: dict = {},
) -> T:
    pass


@overload
def create_obj_from_data(
    data: BaseModel, model: Type[T], db: Session, additional_data: dict = {}, exclude: dict = {}
) -> T:
    pass


def create_obj_from_data(
    data: BaseModel, model: Type[T], db: Session | AsyncSession, additional_data={}, exclude={}
) -> T:
    obj_data = data.model_dump(exclude=exclude) | additional_data
    obj = model(**obj_data)

    async def _create_async_obj():
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    def _create_sync_obj():
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    if isinstance(db, AsyncSession):
        return asyncio.ensure_future(_create_async_obj())  # type: ignore
    elif isinstance(db, Session):
        return _create_sync_obj()
    else:
        raise HTTPException(status_code=404, detail="Invalid session type. Expected Session or AsyncSession.")  # type: ignore


# TODO: Add testing
@overload
async def update_obj_from_data(
    data: BaseModel,
    model: Type[T],
    id: UUID | str,
    db: AsyncSession,
    partial: bool = True,
    ignore_fields: list = [],
    additional_data: dict = {},
    exclude: dict = {},
) -> T:
    pass


@overload
def update_obj_from_data(
    data: BaseModel,
    model: Type[T],
    id: UUID | str,
    db: Session,
    partial: bool = True,
    ignore_fields: list = [],
    additional_data: dict = {},
    exclude: dict = {},
) -> T:
    pass


def update_obj_from_data(
    data: BaseModel,
    model: Type[T],
    id: UUID | str,
    db: Session | AsyncSession,
    partial: bool = True,
    ignore_fields=[],
    additional_data={},
    exclude={},
) -> T:
    def _update_fields(obj: T):
        data_dict = data.model_dump(exclude_unset=partial, exclude=exclude)
        data_dict.update(additional_data)

        for field in data_dict:
            if field not in ignore_fields:
                setattr(obj, field, data_dict[field])

    async def _update_async_obj() -> T:
        obj = await get_object_or_404(model, id, db)
        _update_fields(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    def _update_sync_obj() -> T:
        obj = get_object_or_404(model, id, db)
        _update_fields(obj)
        db.commit()
        db.refresh(obj)
        return obj

    if isinstance(db, AsyncSession):
        return asyncio.ensure_future(_update_async_obj())  # type: ignore
    elif isinstance(db, Session):
        return _update_sync_obj()
    else:
        raise HTTPException(status_code=404, detail="Invalid session type. Expected Session or AsyncSession.")  # type: ignore


# TODO: Add testing
@overload
async def delete_object(db_class: Type[T], id: UUID | str, db: AsyncSession) -> None:
    pass


@overload
def delete_object(db_class: Type[T], id: UUID | str, db: Session) -> None:
    pass


def delete_object(db_class: Type[T], id: UUID | str, db: Session | AsyncSession) -> None:
    async def _delete_async_obj() -> None:
        query = select(db_class).filter(db_class.id == id)
        result = await db.execute(query)
        obj = result.scalar_one_or_none()
        if obj is None:
            raise HTTPException(status_code=404, detail="The object does not exist.")
        await db.delete(obj)
        await db.commit()

    def _delete_sync_obj() -> None:
        obj = db.query(db_class).filter(db_class.id == id).one_or_none()
        if obj is None:
            raise HTTPException(status_code=404, detail="The object does not exist.")
        db.delete(obj)
        db.commit()

    if isinstance(db, AsyncSession):
        return asyncio.ensure_future(_delete_async_obj())  # type: ignore
    elif isinstance(db, Session):
        return _delete_sync_obj()
    else:
        raise HTTPException(status_code=404, detail="Invalid session type. Expected Session or AsyncSession.")  # type: ignore
