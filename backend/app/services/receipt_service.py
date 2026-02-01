"""Receipt service with business logic - SYNC version."""

from typing import Sequence

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.repositories.reaction import ReactionRepository
from app.db.repositories.receipt import EvidenceRepository, ReceiptRepository
from app.db.repositories.topic import TopicRepository
from app.models.db.receipt import EvidenceItem, Receipt
from app.models.db.user import User
from app.models.enums import ReactionType
from app.models.schemas.evidence import EvidenceCreate
from app.models.schemas.receipt import (
    AuthorSummary,
    ReactionCounts,
    ReceiptChain,
    ReceiptChainNode,
    ReceiptCreate,
    ReceiptFork,
    ReceiptResponse,
)

logger = get_logger(__name__)


class ReceiptServiceError(Exception):
    """Base exception for receipt service errors."""

    pass


class ReceiptNotFoundError(ReceiptServiceError):
    """Raised when receipt is not found."""

    pass


class NotAuthorizedError(ReceiptServiceError):
    """Raised when user is not authorized for action."""

    pass


class EvidenceRequiredError(ReceiptServiceError):
    """Raised when receipt would have no evidence."""

    pass


class ReceiptService:
    """Service for receipt-related business logic."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ReceiptRepository(db)
        self.evidence_repo = EvidenceRepository(db)
        self.topic_repo = TopicRepository(db)
        self.reaction_repo = ReactionRepository(db)

    def create_receipt(
        self,
        author: User,
        data: ReceiptCreate,
    ) -> Receipt:
        """Create a new receipt with evidence."""
        # Validate topics exist
        if data.topic_ids:
            topics = self.topic_repo.get_by_ids(data.topic_ids)
            if len(topics) != len(data.topic_ids):
                logger.warning("Some topic IDs not found", topic_ids=data.topic_ids)
        else:
            topics = []

        # Create receipt
        receipt = self.repo.create(
            author_id=author.id,
            claim_text=data.claim_text,
            claim_type=data.claim_type,
            implication_text=data.implication_text,
            visibility=data.visibility,
        )

        # Add topics
        if topics:
            receipt.topics = list(topics)
            self.db.commit()

        # Create evidence items
        for idx, evidence_data in enumerate(data.evidence):
            self.evidence_repo.create(
                receipt_id=receipt.id,
                type=evidence_data.type,
                content_uri=evidence_data.content_uri,
                source_url=evidence_data.source_url,
                captured_at=evidence_data.captured_at,
                caption=evidence_data.caption,
                order_index=idx,
            )

        # Refresh to get all relations
        receipt = self.repo.get_by_id_with_relations(receipt.id)

        logger.info("Receipt created", receipt_id=receipt.id, author_id=author.id)
        return receipt

    def fork_receipt(
        self,
        author: User,
        parent_id: str,
        data: ReceiptFork,
    ) -> Receipt:
        """Create a counter-receipt forking an existing receipt."""
        # Get parent receipt
        parent = self.repo.get_by_id(parent_id)
        if not parent:
            raise ReceiptNotFoundError(f"Receipt {parent_id} not found")

        # Create fork
        receipt = self.repo.create(
            author_id=author.id,
            claim_text=data.claim_text,
            claim_type=data.claim_type,
            implication_text=data.implication_text,
            parent_receipt_id=parent_id,
        )

        # Create evidence items
        for idx, evidence_data in enumerate(data.evidence):
            self.evidence_repo.create(
                receipt_id=receipt.id,
                type=evidence_data.type,
                content_uri=evidence_data.content_uri,
                source_url=evidence_data.source_url,
                captured_at=evidence_data.captured_at,
                caption=evidence_data.caption,
                order_index=idx,
            )

        # Update parent fork count
        self.repo.increment_fork_count(parent_id)

        # Refresh to get all relations
        receipt = self.repo.get_by_id_with_relations(receipt.id)

        logger.info(
            "Receipt forked",
            receipt_id=receipt.id,
            parent_id=parent_id,
            author_id=author.id,
        )
        return receipt

    def get_receipt(self, receipt_id: str) -> Receipt | None:
        """Get a receipt by ID with all relations."""
        return self.repo.get_by_id_with_relations(receipt_id)

    def delete_receipt(self, receipt_id: str, user: User) -> None:
        """Delete a receipt (author only)."""
        receipt = self.repo.get_by_id(receipt_id)

        if not receipt:
            raise ReceiptNotFoundError(f"Receipt {receipt_id} not found")

        if receipt.author_id != user.id and not user.is_moderator:
            raise NotAuthorizedError("Not authorized to delete this receipt")

        self.repo.delete(receipt)
        logger.info("Receipt deleted", receipt_id=receipt_id, deleted_by=user.id)

    def add_evidence(
        self,
        receipt_id: str,
        user: User,
        data: EvidenceCreate,
    ) -> EvidenceItem:
        """Add evidence to an existing receipt."""
        receipt = self.repo.get_by_id(receipt_id)

        if not receipt:
            raise ReceiptNotFoundError(f"Receipt {receipt_id} not found")

        if receipt.author_id != user.id:
            raise NotAuthorizedError("Not authorized to modify this receipt")

        # Get next order index
        max_idx = self.evidence_repo.get_max_order_index(receipt_id)

        evidence = self.evidence_repo.create(
            receipt_id=receipt_id,
            type=data.type,
            content_uri=data.content_uri,
            source_url=data.source_url,
            captured_at=data.captured_at,
            caption=data.caption,
            order_index=max_idx + 1,
        )

        logger.info(
            "Evidence added",
            evidence_id=evidence.id,
            receipt_id=receipt_id,
        )
        return evidence

    def remove_evidence(
        self,
        receipt_id: str,
        evidence_id: str,
        user: User,
    ) -> None:
        """Remove evidence from a receipt."""
        receipt = self.repo.get_by_id(receipt_id)

        if not receipt:
            raise ReceiptNotFoundError(f"Receipt {receipt_id} not found")

        if receipt.author_id != user.id:
            raise NotAuthorizedError("Not authorized to modify this receipt")

        evidence = self.evidence_repo.get_by_id(evidence_id)
        if not evidence or evidence.receipt_id != receipt_id:
            raise ReceiptNotFoundError(f"Evidence {evidence_id} not found")

        # Check if this is the last evidence item
        count = self.evidence_repo.count_by_receipt(receipt_id)
        if count <= 1:
            raise EvidenceRequiredError("Cannot remove last evidence item")

        self.evidence_repo.delete(evidence)
        logger.info(
            "Evidence removed",
            evidence_id=evidence_id,
            receipt_id=receipt_id,
        )

    def get_chain(
        self,
        receipt_id: str,
        max_depth: int = 3,
    ) -> ReceiptChain | None:
        """Get a receipt with its fork chain."""
        root, forks = self.repo.get_chain(receipt_id, max_depth=max_depth)

        if not root:
            return None

        # Build response
        root_response = self._receipt_to_response(root)

        # Build fork tree
        fork_nodes = self._build_fork_tree(root.id, forks)

        return ReceiptChain(
            root=root_response,
            forks=fork_nodes,
            total_in_chain=1 + len(forks),
        )

    def _build_fork_tree(
        self,
        parent_id: str,
        all_forks: list[Receipt],
    ) -> list[ReceiptChainNode]:
        """Build nested fork tree structure."""
        direct_forks = [f for f in all_forks if f.parent_receipt_id == parent_id]

        nodes = []
        for fork in direct_forks:
            child_nodes = self._build_fork_tree(fork.id, all_forks)
            nodes.append(
                ReceiptChainNode(
                    id=fork.id,
                    parent_receipt_id=fork.parent_receipt_id,
                    claim_text=fork.claim_text,
                    author=self._author_summary(fork.author),
                    evidence=[],  # Simplified for chain view
                    reactions=self._get_reaction_counts(fork.id),
                    forks=child_nodes,
                    created_at=fork.created_at,
                )
            )

        return nodes

    def get_by_author(
        self,
        author_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> Sequence[Receipt]:
        """Get receipts by author."""
        return self.repo.get_by_author(author_id, skip=skip, limit=limit)

    def _receipt_to_response(self, receipt: Receipt) -> ReceiptResponse:
        """Convert Receipt model to ReceiptResponse schema."""
        from app.models.schemas.evidence import EvidenceResponse

        return ReceiptResponse(
            id=receipt.id,
            author=self._author_summary(receipt.author),
            claim_text=receipt.claim_text,
            claim_type=receipt.claim_type,
            implication_text=receipt.implication_text,
            parent_receipt_id=receipt.parent_receipt_id,
            topic_ids=[t.id for t in receipt.topics] if receipt.topics else [],
            visibility=receipt.visibility,
            evidence=[
                EvidenceResponse(
                    id=e.id,
                    type=e.type,
                    content_uri=e.content_uri,
                    source_url=e.source_url,
                    captured_at=e.captured_at,
                    caption=e.caption,
                    order_index=e.order_index,
                    created_at=e.created_at,
                )
                for e in receipt.evidence_items
            ],
            reactions=self._get_reaction_counts(receipt.id),
            fork_count=receipt.fork_count,
            created_at=receipt.created_at,
            updated_at=receipt.updated_at,
        )

    def _author_summary(self, author: User) -> AuthorSummary:
        """Convert User to AuthorSummary."""
        return AuthorSummary(
            id=author.id,
            handle=author.handle,
            display_name=author.display_name,
            avatar_url=author.avatar_url,
        )

    def _get_reaction_counts(self, receipt_id: str) -> ReactionCounts:
        """Get reaction counts for a receipt."""
        counts = self.reaction_repo.get_reaction_counts(receipt_id)
        return ReactionCounts(
            support=counts.get(ReactionType.SUPPORT, 0),
            dispute=counts.get(ReactionType.DISPUTE, 0),
            bookmark=counts.get(ReactionType.BOOKMARK, 0),
        )
