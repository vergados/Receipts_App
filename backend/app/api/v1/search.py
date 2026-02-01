"""Search API endpoints."""

from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.models.schemas.base import PaginationInfo
from app.models.schemas.feed import FeedResponse
from app.db.repositories.receipt import ReceiptRepository
from app.services.receipt_service import ReceiptService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=FeedResponse)
def search_receipts(
    db: DbSession,
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    cursor: str | None = None,
) -> FeedResponse:
    """Search receipts by claim text, implication, or author."""
    repo = ReceiptRepository(db)
    receipt_service = ReceiptService(db)

    # Decode cursor
    skip = 0
    if cursor:
        try:
            skip = int(cursor)
        except ValueError:
            skip = 0

    receipts = repo.search(q, skip=skip, limit=limit + 1)

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
