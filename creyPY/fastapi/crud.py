from typing import Type, TypeVar
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .models.base import Base

T = TypeVar("T", bound=Base)


def get_object_or_404(
    db_class: Type[T], id: UUID | str, db: Session, expunge: bool = False, lookup_column: str = "id"
) -> T:
    obj = db.query(db_class).filter(getattr(db_class, lookup_column) == id).one_or_none()
    if obj is None:
        raise HTTPException(status_code=404, detail="The object does not exist.")
    if expunge:
        db.expunge(obj)
    return obj


# TODO: Add testing
def create_obj_from_data(
    data: BaseModel, model: Type[T], db: Session, additional_data={}, exclude={}
) -> T:
    obj = model(**data.model_dump(exclude=exclude) | additional_data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# TODO: Add testing
def update_obj_from_data(
    data: BaseModel,
    model: Type[T],
    id: UUID | str,
    db: Session,
    partial: bool = True,
    ignore_fields=[],
    additional_data={},
    exclude={},
) -> T:
    obj = get_object_or_404(model, id, db)
    data_dict = data.model_dump(exclude_unset=partial, exclude=exclude)
    data_dict.update(additional_data)  # merge additional_data into data_dict
    for field in data_dict:
        if field not in ignore_fields:
            setattr(obj, field, data_dict[field])
    db.commit()
    db.refresh(obj)
    return obj


# TODO: Add testing
def delete_object(db_class: Type[T], id: UUID | str, db: Session) -> None:
    obj = db.query(db_class).filter(db_class.id == id).one_or_none()
    if obj is None:
        raise HTTPException(status_code=404, detail="The object does not exist.")
    db.delete(obj)
    db.commit()
