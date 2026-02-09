"""Export service for receipt card generation - SYNC version."""

from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.db.repositories.export import ExportRepository
from app.db.repositories.receipt import ReceiptRepository
from app.models.db.export import Export
from app.models.db.user import User
from app.models.enums import ExportFormat, ExportStatus
from app.models.schemas.export import ExportCreate

logger = get_logger(__name__)


class ExportServiceError(Exception):
    """Base exception for export service errors."""

    pass


class ReceiptNotFoundError(ExportServiceError):
    """Raised when receipt is not found."""

    pass


class ExportService:
    """Service for receipt card export."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ExportRepository(db)
        self.receipt_repo = ReceiptRepository(db)

    def create_export(
        self,
        user: User,
        receipt_id: str,
        data: ExportCreate,
    ) -> Export:
        """Create an export job for a receipt card."""
        # Verify receipt exists
        receipt = self.receipt_repo.get_by_id_with_relations(receipt_id)
        if not receipt:
            raise ReceiptNotFoundError(f"Receipt {receipt_id} not found")

        # Create export record
        export = self.repo.create(
            receipt_id=receipt_id,
            user_id=user.id,
            format=data.format,
            include_evidence_thumbnails=data.include_evidence_thumbnails,
            include_chain_preview=data.include_chain_preview,
            status=ExportStatus.PROCESSING,
        )

        logger.info(
            "Export created",
            export_id=export.id,
            receipt_id=receipt_id,
            format=data.format.value,
        )

        return export

    def get_export(self, export_id: str) -> Export | None:
        """Get export by ID."""
        return self.repo.get_by_id_with_relations(export_id)

    def _process_export(self, export: Export) -> None:
        """Process an export job (generate the receipt card)."""
        try:
            # Get receipt with relations
            receipt = self.receipt_repo.get_by_id_with_relations(export.receipt_id)
            if not receipt:
                raise ReceiptNotFoundError(f"Receipt {export.receipt_id} not found")

            # Generate the card image
            image_bytes = self._generate_card_image(
                receipt,
                include_evidence=export.include_evidence_thumbnails,
                include_chain=export.include_chain_preview,
            )

            # Save to storage
            filename = f"receipt_card_{receipt.id}.png"
            storage_path = self._save_to_storage(filename, image_bytes)

            # Update export record
            export.status = ExportStatus.COMPLETED
            export.download_url = storage_path
            export.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
            self.db.commit()

            logger.info("Export completed", export_id=export.id)

        except Exception as e:
            logger.error("Export failed", export_id=export.id, error=str(e))
            export.status = ExportStatus.FAILED
            export.error_message = str(e)[:500]
            self.db.commit()

    def _generate_card_image(
        self,
        receipt,
        include_evidence: bool = True,
        include_chain: bool = False,
    ) -> bytes:
        """Generate receipt card image using Pillow."""
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            # Fallback if Pillow not available - return placeholder
            logger.warning("Pillow not available, returning placeholder")
            return self._generate_placeholder()

        # Card dimensions
        width = settings.export_card_width
        height = 630  # 1.91:1 aspect ratio (good for social sharing)
        padding = 40

        # Create image with white background
        img = Image.new("RGB", (width, height), color="#FFFFFF")
        draw = ImageDraw.Draw(img)

        # Try to use a nice font, fall back to default
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except (IOError, OSError):
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # Draw header bar
        draw.rectangle([(0, 0), (width, 80)], fill="#1a1a2e")
        draw.text(
            (padding, 25),
            "RECEIPT",
            font=title_font,
            fill="#FFFFFF",
        )

        # Draw claim
        y_pos = 100
        draw.text(
            (padding, y_pos),
            "CLAIM",
            font=small_font,
            fill="#666666",
        )
        y_pos += 30

        # Word wrap claim text
        claim_text = receipt.claim_text[:300] + "..." if len(receipt.claim_text) > 300 else receipt.claim_text
        lines = self._wrap_text(claim_text, body_font, width - padding * 2)
        for line in lines[:4]:  # Max 4 lines
            draw.text((padding, y_pos), line, font=body_font, fill="#1a1a2e")
            y_pos += 30

        # Draw evidence count
        y_pos += 20
        evidence_count = len(receipt.evidence_items) if receipt.evidence_items else 0
        draw.text(
            (padding, y_pos),
            f"📎 {evidence_count} evidence item{'s' if evidence_count != 1 else ''}",
            font=small_font,
            fill="#666666",
        )

        # Draw footer with author and timestamp
        footer_y = height - 60
        draw.line([(padding, footer_y - 20), (width - padding, footer_y - 20)], fill="#EEEEEE", width=1)

        author_text = f"@{receipt.author.handle}"
        timestamp = receipt.created_at.strftime("%Y-%m-%d %H:%M UTC")
        draw.text((padding, footer_y), author_text, font=small_font, fill="#1a1a2e")
        draw.text((width - padding - 200, footer_y), timestamp, font=small_font, fill="#666666")

        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer, format="PNG", quality=settings.export_card_quality)
        return buffer.getvalue()

    def _wrap_text(self, text: str, font, max_width: int) -> list[str]:
        """Simple word wrap for text."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            line = " ".join(current_line)
            # Rough estimate of text width
            if len(line) * 10 > max_width:
                current_line.pop()
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def _generate_placeholder(self) -> bytes:
        """Generate a simple placeholder image."""
        # 1x1 white pixel PNG
        return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xa7V\xa8\x00\x00\x00\x00IEND\xaeB`\x82'

    def _save_to_storage(self, filename: str, data: bytes) -> str:
        """Save file to storage and return URL."""
        # For v1, save locally
        storage_dir = Path(settings.storage_local_path) / "exports"
        storage_dir.mkdir(parents=True, exist_ok=True)

        file_path = storage_dir / filename
        file_path.write_bytes(data)

        # Return relative path (would be full URL in production)
        return f"/exports/{filename}"


def process_export_job(export_id: str) -> None:
    """Background task: process an export in its own DB session.

    This runs AFTER the response is sent, so the request's DB session is closed.
    We open a new session via SessionLocal.
    """
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        service = ExportService(db)
        export = service.repo.get_by_id(export_id)
        if export:
            service._process_export(export)
        else:
            logger.error("Export not found for background processing", export_id=export_id)
    finally:
        db.close()
