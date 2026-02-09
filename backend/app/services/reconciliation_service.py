"""Counter reconciliation service — fixes denormalized counts on receipts."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logging import get_logger

logger = get_logger(__name__)


def reconcile_counts(db: Session) -> dict[str, int]:
    """Reconcile reaction_count and fork_count on all receipts.

    Returns a dict with the number of rows updated for each counter.
    """
    reaction_result = db.execute(text(
        "UPDATE receipts SET reaction_count = ("
        "  SELECT COUNT(*) FROM reactions WHERE reactions.receipt_id = receipts.id"
        ")"
    ))
    reaction_updated = reaction_result.rowcount

    fork_result = db.execute(text(
        "UPDATE receipts SET fork_count = ("
        "  SELECT COUNT(*) FROM receipts AS f WHERE f.parent_receipt_id = receipts.id"
        ")"
    ))
    fork_updated = fork_result.rowcount

    db.commit()

    logger.info(
        "Counter reconciliation complete",
        reaction_rows=reaction_updated,
        fork_rows=fork_updated,
    )

    return {"reaction_rows": reaction_updated, "fork_rows": fork_updated}
