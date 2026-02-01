"""Reaction-related Pydantic schemas."""

from datetime import datetime

from app.models.enums import ReactionType
from app.models.schemas.base import BaseSchema, TimestampMixin


class ReactionCreate(BaseSchema):
    """Schema for creating a reaction."""
    
    type: ReactionType


class ReactionResponse(BaseSchema, TimestampMixin):
    """Schema for reaction in responses."""
    
    id: str
    receipt_id: str
    user_id: str
    type: ReactionType
