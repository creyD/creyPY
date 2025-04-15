from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# The created_by_id is a string because we use the sub from Auth0
class BaseSchemaModelIN(BaseModel):
    created_by_id: str
    model_config = ConfigDict(from_attributes=True)


class BaseSchemaModelOUT(BaseSchemaModelIN):
    id: UUID
    created_at: datetime
    updated_at: datetime
