"""Base Pydantic schemas with common configuration."""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for models with timestamps."""
    
    created_at: datetime


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response wrapper."""
    
    items: list[T]
    pagination: "PaginationInfo"


class PaginationInfo(BaseSchema):
    """Pagination metadata."""
    
    next_cursor: str | None = None
    has_more: bool = False


class ErrorDetail(BaseSchema):
    """Error detail structure."""
    
    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseSchema):
    """Standard error response."""
    
    error: ErrorDetail
