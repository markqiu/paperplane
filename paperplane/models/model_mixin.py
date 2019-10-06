from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Schema, validator


class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime] = Schema(..., alias="createdAt")
    updated_at: Optional[datetime] = Schema(..., alias="updatedAt")


class DBModelMixin(DateTimeModelMixin):
    id: Optional[Any] = Schema(..., alias="_id")

    @validator("id")
    def validate_id(cls, id):
        return str(id)
