from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

# The created_by_id is a string because we use the sub from Auth0
class BaseSchemaModelIN(BaseModel):
    created_by_id: str
    model_config = ConfigDict(from_attributes=True)


class BaseSchemaModelOUT(BaseSchemaModelIN):
    id: str = Field(
        ...
    )
    created_at: datetime
    updated_at: datetime

    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, value):
        if isinstance(value, UUID):
            return str(value)
        return value
