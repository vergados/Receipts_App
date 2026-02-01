"""Feed-related Pydantic schemas."""

from typing import Literal

from pydantic import Field

from app.models.schemas.base import BaseSchema, PaginationInfo
from app.models.schemas.receipt import ReceiptResponse, ReceiptSummary
from app.models.schemas.topic import TopicResponse


class FeedQuery(BaseSchema):
    """Query parameters for feed endpoints."""
    
    limit: int = Field(20, ge=1, le=100)
    cursor: str | None = None


class TrendingQuery(BaseSchema):
    """Query parameters for trending endpoint."""
    
    limit: int = Field(20, ge=1, le=100)
    period: Literal["hour", "day", "week", "month"] = "day"


class TopicFeedQuery(BaseSchema):
    """Query parameters for topic feed."""
    
    limit: int = Field(20, ge=1, le=100)
    cursor: str | None = None
    sort: Literal["recent", "trending"] = "recent"


class TrendingChain(BaseSchema):
    """A trending receipt chain."""
    
    root_receipt: ReceiptSummary
    fork_count: int
    engagement_score: int
    top_fork: ReceiptSummary | None = None


class FeedResponse(BaseSchema):
    """Paginated feed response."""
    
    receipts: list[ReceiptResponse]
    pagination: PaginationInfo


class TrendingResponse(BaseSchema):
    """Trending chains response."""
    
    chains: list[TrendingChain]


class TopicFeedResponse(BaseSchema):
    """Topic feed response with topic details."""
    
    topic: TopicResponse
    receipts: list[ReceiptResponse]
    pagination: PaginationInfo
