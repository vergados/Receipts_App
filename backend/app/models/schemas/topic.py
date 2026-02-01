"""Topic-related Pydantic schemas."""

from pydantic import Field

from app.models.schemas.base import BaseSchema, TimestampMixin


class TopicBase(BaseSchema):
    """Base topic fields."""
    
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class TopicCreate(TopicBase):
    """Schema for creating a topic (admin only)."""
    
    pass


class TopicResponse(TopicBase, TimestampMixin):
    """Schema for topic in responses."""
    
    id: str
    receipt_count: int = 0


class TopicListResponse(BaseSchema):
    """Schema for list of topics."""
    
    topics: list[TopicResponse]
