import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative
from sqlalchemy.sql import func

from .mixins import AutoAnnotateMixin, AutoInitMixin


@as_declarative()
class Base(AutoAnnotateMixin, AutoInitMixin):
    __abstract__ = True
    # Primary key as uuid
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(String)

    __name__: str

    # TODO: Add automated foreign key resolution

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def __str__(self) -> str:
        # if the object has a name, title or similar attribute, return it
        if hasattr(self, "name"):
            return str(self.name)  # type: ignore

        # if the object has a title attribute, return it
        if hasattr(self, "title"):
            return str(self.title)  # type: ignore

        # otherwise return the object's id
        return str(self.id)
