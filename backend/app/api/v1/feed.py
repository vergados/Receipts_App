"""Feed API endpoints - SYNC version."""

from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from app.core.dependencies import CurrentUserOptional, DbSession
from app.models.schemas.base import PaginationInfo
from app.models.schemas.feed import (
    FeedResponse,
    TopicFeedResponse,
    TrendingChain,
    TrendingResponse,
)
from app.models.schemas.receipt import ReactionCounts, ReceiptSummary
from app.services.feed_service import FeedService
from app.services.receipt_service import ReceiptService
from app.services.topic_service import TopicService

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("", response_model=FeedResponse)
def get_feed(
    db: DbSession,
    user: CurrentUserOptional,
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = None,
) -> FeedResponse:
    """Get personalized home feed."""
    service = FeedService(db)
    receipt_service = ReceiptService(db)

    # Decode cursor
    skip = 0
    if cursor:
        try:
            skip = int(cursor)
        except ValueError:
            skip = 0

    receipts = service.get_home_feed(user=user, skip=skip, limit=limit + 1)

    has_more = len(receipts) > limit
    if has_more:
        receipts = receipts[:limit]

    receipt_responses = [
        receipt_service._receipt_to_response(r) for r in receipts
    ]

    return FeedResponse(
        receipts=receipt_responses,
        pagination=PaginationInfo(
            next_cursor=str(skip + limit) if has_more else None,
            has_more=has_more,
        ),
    )


@router.get("/trending", response_model=TrendingResponse)
def get_trending(
    db: DbSession,
    limit: int = Query(20, ge=1, le=100),
    period: Literal["hour", "day", "week", "month"] = "day",
) -> TrendingResponse:
    """Get trending receipt chains."""
    service = FeedService(db)
    receipt_service = ReceiptService(db)

    # Map period to hours
    period_hours = {
        "hour": 1,
        "day": 24,
        "week": 168,
        "month": 720,
    }

    receipts = service.get_trending(limit=limit, hours=period_hours[period])

    # Convert to trending chains
    chains = []
    for receipt in receipts:
        chains.append(
            TrendingChain(
                root_receipt=ReceiptSummary(
                    id=receipt.id,
                    author=receipt_service._author_summary(receipt.author),
                    claim_text=receipt.claim_text,
                    evidence_count=len(receipt.evidence_items) if receipt.evidence_items else 0,
                    reactions=receipt_service._get_reaction_counts(receipt.id),
                    fork_count=receipt.fork_count,
                    created_at=receipt.created_at,
                ),
                fork_count=receipt.fork_count,
                engagement_score=receipt.reaction_count + receipt.fork_count * 2,
                top_fork=None,  # TODO: get top fork
            )
        )

    return TrendingResponse(chains=chains)


@router.get("/topic/{slug}", response_model=TopicFeedResponse)
def get_topic_feed(
    slug: str,
    db: DbSession,
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = None,
    sort: Literal["recent", "trending"] = "recent",
) -> TopicFeedResponse:
    """Get receipts for a specific topic."""
    feed_service = FeedService(db)
    receipt_service = ReceiptService(db)
    topic_service = TopicService(db)

    # Decode cursor
    skip = 0
    if cursor:
        try:
            skip = int(cursor)
        except ValueError:
            skip = 0

    receipts, topic = feed_service.get_topic_feed(slug, skip=skip, limit=limit + 1)

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Topic '{slug}' not found",
                }
            },
        )

    has_more = len(receipts) > limit
    if has_more:
        receipts = receipts[:limit]

    receipt_count = topic_service.get_receipt_count(topic.id)

    return TopicFeedResponse(
        topic=topic_service.topic_to_response(topic, receipt_count),
        receipts=[receipt_service._receipt_to_response(r) for r in receipts],
        pagination=PaginationInfo(
            next_cursor=str(skip + limit) if has_more else None,
            has_more=has_more,
        ),
    )
