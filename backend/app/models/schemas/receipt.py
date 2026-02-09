"""Receipt-related Pydantic schemas."""

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from app.models.enums import ClaimType, Visibility
from app.models.schemas.base import BaseSchema, PaginationInfo, TimestampMixin
from app.models.schemas.evidence import EvidenceCreate, EvidenceResponse
from app.models.schemas.user import UserPublic


class ReactionCounts(BaseSchema):
    """Aggregated reaction counts."""
    
    support: int = 0
    dispute: int = 0
    bookmark: int = 0


class AuthorSummary(BaseSchema):
    """Minimal author info for receipt display."""
    
    id: str
    handle: str
    display_name: str
    avatar_url: str | None = None


class ReceiptCreate(BaseSchema):
    """Schema for creating a receipt."""

    claim_text: str = Field(..., min_length=1, max_length=1000)
    claim_type: ClaimType = ClaimType.TEXT
    implication_text: str | None = Field(None, max_length=1000)
    topic_ids: list[str] = Field(default_factory=list, max_length=5)
    visibility: Visibility = Visibility.PUBLIC
    evidence: list[EvidenceCreate] = Field(..., min_length=1, max_length=10)

    # Newsroom features (optional)
    organization_id: str | None = None
    is_breaking_news: bool = False
    investigation_thread_id: str | None = None

    @field_validator("evidence")
    @classmethod
    def validate_evidence(cls, v: list[EvidenceCreate]) -> list[EvidenceCreate]:
        if len(v) < 1:
            raise ValueError("At least one evidence item is required")
        if len(v) > 10:
            raise ValueError("Maximum 10 evidence items allowed")
        return v


class ReceiptFork(BaseSchema):
    """Schema for forking (counter-receipt) a receipt."""
    
    claim_text: str = Field(..., min_length=1, max_length=1000)
    claim_type: ClaimType = ClaimType.TEXT
    implication_text: str | None = Field(None, max_length=1000)
    evidence: list[EvidenceCreate] = Field(..., min_length=1, max_length=10)


class ReceiptResponse(BaseSchema, TimestampMixin):
    """Schema for receipt in responses."""

    id: str
    author: AuthorSummary
    claim_text: str
    claim_type: ClaimType
    implication_text: str | None = None
    parent_receipt_id: str | None = None
    topic_ids: list[str] = []
    visibility: Visibility
    evidence: list[EvidenceResponse] = []
    reactions: ReactionCounts = ReactionCounts()
    fork_count: int = 0
    updated_at: datetime | None = None

    # Newsroom features (optional, for backward compatibility)
    organization_id: str | None = None
    is_breaking_news: bool = False
    investigation_thread_id: str | None = None


class ReceiptSummary(BaseSchema, TimestampMixin):
    """Minimal receipt info for lists and previews."""
    
    id: str
    author: AuthorSummary
    claim_text: str
    evidence_count: int = 0
    reactions: ReactionCounts = ReactionCounts()
    fork_count: int = 0


class ReceiptChain(BaseSchema):
    """Receipt with its fork tree."""
    
    root: ReceiptResponse
    forks: list["ReceiptChainNode"] = []
    total_in_chain: int = 1


class ReceiptChainNode(BaseSchema):
    """Node in a receipt fork tree."""
    
    id: str
    parent_receipt_id: str
    claim_text: str
    author: AuthorSummary
    evidence: list[EvidenceResponse] = []
    reactions: ReactionCounts = ReactionCounts()
    forks: list["ReceiptChainNode"] = []
    created_at: datetime


class ReceiptListResponse(BaseSchema):
    """Paginated list of receipts."""
    
    receipts: list[ReceiptResponse]
    pagination: PaginationInfo


# Update forward references
ReceiptChain.model_rebuild()
ReceiptChainNode.model_rebuild()
