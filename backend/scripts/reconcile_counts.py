"""CLI script to reconcile denormalized counters on receipts.

Usage:
    cd backend
    ./venv/bin/python -m scripts.reconcile_counts
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import SessionLocal
from app.services.reconciliation_service import reconcile_counts


def main() -> None:
    print("Starting counter reconciliation...")
    db = SessionLocal()
    try:
        result = reconcile_counts(db)
        print(f"Done. Reaction rows updated: {result['reaction_rows']}, Fork rows updated: {result['fork_rows']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
