from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchemaModelIN(BaseModel):
    created_by_id: str
    model_config = ConfigDict(from_attributes=True)


class BaseSchemaModelOUT(BaseSchemaModelIN):
    id: UUID
    created_at: datetime
    updated_at: datetime
