"""Evidence API endpoints - SYNC version."""

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession
from app.models.schemas.evidence import EvidenceCreate, EvidenceResponse
from app.services.receipt_service import (
    EvidenceRequiredError,
    NotAuthorizedError,
    ReceiptNotFoundError,
    ReceiptService,
)

router = APIRouter(prefix="/receipts/{receipt_id}/evidence", tags=["evidence"])


@router.post("", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
def add_evidence(
    receipt_id: str,
    data: EvidenceCreate,
    user: CurrentUser,
    db: DbSession,
) -> EvidenceResponse:
    """Add evidence to an existing receipt."""
    service = ReceiptService(db)

    try:
        evidence = service.add_evidence(receipt_id, user, data)
        return EvidenceResponse(
            id=evidence.id,
            type=evidence.type,
            content_uri=evidence.content_uri,
            source_url=evidence.source_url,
            captured_at=evidence.captured_at,
            caption=evidence.caption,
            order_index=evidence.order_index,
            created_at=evidence.created_at,
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
    except NotAuthorizedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Not authorized to modify this receipt",
                }
            },
        )


@router.delete("/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_evidence(
    receipt_id: str,
    evidence_id: str,
    user: CurrentUser,
    db: DbSession,
) -> None:
    """Remove evidence from a receipt."""
    service = ReceiptService(db)

    try:
        service.remove_evidence(receipt_id, evidence_id, user)
    except ReceiptNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Receipt or evidence not found",
                }
            },
        )
    except NotAuthorizedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Not authorized to modify this receipt",
                }
            },
        )
    except EvidenceRequiredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "EVIDENCE_REQUIRED",
                    "message": "Cannot remove last evidence item",
                }
            },
        )
