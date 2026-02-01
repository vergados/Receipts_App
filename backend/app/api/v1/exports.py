"""Exports API endpoints - SYNC version."""

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession
from app.models.schemas.export import ExportCreate, ExportResponse
from app.services.export_service import ExportService, ReceiptNotFoundError

router = APIRouter(tags=["exports"])


@router.post(
    "/receipts/{receipt_id}/export",
    response_model=ExportResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_export(
    receipt_id: str,
    data: ExportCreate,
    user: CurrentUser,
    db: DbSession,
) -> ExportResponse:
    """Generate exportable receipt card."""
    service = ExportService(db)

    try:
        export = service.create_export(user, receipt_id, data)
        return ExportResponse(
            export_id=export.id,
            status=export.status,
            estimated_seconds=5 if export.status.value == "processing" else None,
            download_url=export.download_url,
            expires_at=export.expires_at,
            format=export.format,
            error_message=export.error_message,
            created_at=export.created_at,
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


@router.get("/exports/{export_id}", response_model=ExportResponse)
def get_export(
    export_id: str,
    user: CurrentUser,
    db: DbSession,
) -> ExportResponse:
    """Get export status and download URL."""
    service = ExportService(db)
    export = service.get_export(export_id)

    if not export:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Export {export_id} not found",
                }
            },
        )

    # Verify user owns this export
    if export.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Not authorized to view this export",
                }
            },
        )

    return ExportResponse(
        export_id=export.id,
        status=export.status,
        download_url=export.download_url,
        expires_at=export.expires_at,
        format=export.format,
        error_message=export.error_message,
        created_at=export.created_at,
    )
