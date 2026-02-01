"""Reactions API endpoints - SYNC version."""

from fastapi import APIRouter, HTTPException, Query, status

from app.core.dependencies import CurrentUser, DbSession
from app.models.enums import ReactionType
from app.models.schemas.reaction import ReactionCreate, ReactionResponse
from app.services.reaction_service import ReactionService, ReceiptNotFoundError

router = APIRouter(prefix="/receipts/{receipt_id}/reactions", tags=["reactions"])


@router.post("", response_model=ReactionResponse, status_code=status.HTTP_201_CREATED)
def add_reaction(
    receipt_id: str,
    data: ReactionCreate,
    user: CurrentUser,
    db: DbSession,
) -> ReactionResponse:
    """Add reaction to a receipt."""
    service = ReactionService(db)

    try:
        reaction = service.add_reaction(user, receipt_id, data.type)
        return ReactionResponse(
            id=reaction.id,
            receipt_id=reaction.receipt_id,
            user_id=reaction.user_id,
            type=reaction.type,
            created_at=reaction.created_at,
        )
    except ReceiptNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Receipt {receipt_id} not found",
                }
            },
        )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def remove_reaction(
    receipt_id: str,
    user: CurrentUser,
    db: DbSession,
    type: ReactionType = Query(..., description="Reaction type to remove"),
) -> None:
    """Remove user's reaction from a receipt."""
    service = ReactionService(db)
    service.remove_reaction(user, receipt_id, type)
