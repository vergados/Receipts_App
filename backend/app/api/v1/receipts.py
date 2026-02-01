"""Receipts API endpoints - SYNC version."""

from fastapi import APIRouter, HTTPException, Query, status

from app.core.dependencies import CurrentUser, DbSession
from app.models.schemas.receipt import (
    ReceiptChain,
    ReceiptCreate,
    ReceiptFork,
    ReceiptResponse,
)
from app.services.receipt_service import (
    NotAuthorizedError,
    ReceiptNotFoundError,
    ReceiptService,
)

router = APIRouter(prefix="/receipts", tags=["receipts"])


@router.post("", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
def create_receipt(
    data: ReceiptCreate,
    user: CurrentUser,
    db: DbSession,
) -> ReceiptResponse:
    """Create a new receipt."""
    service = ReceiptService(db)
    receipt = service.create_receipt(user, data)
    return service._receipt_to_response(receipt)


@router.get("/{receipt_id}", response_model=ReceiptResponse)
def get_receipt(receipt_id: str, db: DbSession) -> ReceiptResponse:
    """Get a receipt by ID."""
    service = ReceiptService(db)
    receipt = service.get_receipt(receipt_id)

    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Receipt {receipt_id} not found",
                }
            },
        )

    return service._receipt_to_response(receipt)


@router.delete("/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_receipt(
    receipt_id: str,
    user: CurrentUser,
    db: DbSession,
) -> None:
    """Delete a receipt (author only)."""
    service = ReceiptService(db)

    try:
        service.delete_receipt(receipt_id, user)
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
    except NotAuthorizedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Not authorized to delete this receipt",
                }
            },
        )


@router.post("/{receipt_id}/fork", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
def fork_receipt(
    receipt_id: str,
    data: ReceiptFork,
    user: CurrentUser,
    db: DbSession,
) -> ReceiptResponse:
    """Create a counter-receipt forking an existing receipt."""
    service = ReceiptService(db)

    try:
        receipt = service.fork_receipt(user, receipt_id, data)
        return service._receipt_to_response(receipt)
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


@router.get("/{receipt_id}/chain", response_model=ReceiptChain)
def get_receipt_chain(
    receipt_id: str,
    db: DbSession,
    depth: int = Query(3, ge=1, le=10),
) -> ReceiptChain:
    """Get the full chain of receipts (original + forks)."""
    service = ReceiptService(db)
    chain = service.get_chain(receipt_id, max_depth=depth)

    if not chain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Receipt {receipt_id} not found",
                }
            },
        )

    return chain
