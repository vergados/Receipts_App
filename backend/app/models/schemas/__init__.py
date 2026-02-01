"""Pydantic schemas package."""

from app.models.schemas.auth import (
    AccessTokenResponse,
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
)
from app.models.schemas.base import (
    BaseSchema,
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
    PaginationInfo,
)
from app.models.schemas.evidence import EvidenceCreate, EvidenceResponse
from app.models.schemas.export import ExportCreate, ExportResponse
from app.models.schemas.feed import (
    FeedQuery,
    FeedResponse,
    TopicFeedQuery,
    TopicFeedResponse,
    TrendingChain,
    TrendingQuery,
    TrendingResponse,
)
from app.models.schemas.moderation import BlockResponse, ReportCreate, ReportResponse
from app.models.schemas.reaction import ReactionCreate, ReactionResponse
from app.models.schemas.receipt import (
    AuthorSummary,
    ReactionCounts,
    ReceiptChain,
    ReceiptChainNode,
    ReceiptCreate,
    ReceiptFork,
    ReceiptListResponse,
    ReceiptResponse,
    ReceiptSummary,
)
from app.models.schemas.topic import (
    TopicCreate,
    TopicListResponse,
    TopicResponse,
)
from app.models.schemas.upload import UploadRequest, UploadResponse
from app.models.schemas.user import (
    UserCreate,
    UserPrivate,
    UserPublic,
    UserUpdate,
)

__all__ = [
    # Base
    "BaseSchema",
    "ErrorDetail",
    "ErrorResponse",
    "PaginatedResponse",
    "PaginationInfo",
    # Auth
    "LoginRequest",
    "TokenResponse",
    "RefreshRequest",
    "AccessTokenResponse",
    "AuthResponse",
    # User
    "UserCreate",
    "UserUpdate",
    "UserPublic",
    "UserPrivate",
    # Receipt
    "ReceiptCreate",
    "ReceiptFork",
    "ReceiptResponse",
    "ReceiptSummary",
    "ReceiptChain",
    "ReceiptChainNode",
    "ReceiptListResponse",
    "AuthorSummary",
    "ReactionCounts",
    # Evidence
    "EvidenceCreate",
    "EvidenceResponse",
    # Topic
    "TopicCreate",
    "TopicResponse",
    "TopicListResponse",
    # Reaction
    "ReactionCreate",
    "ReactionResponse",
    # Feed
    "FeedQuery",
    "FeedResponse",
    "TrendingQuery",
    "TrendingResponse",
    "TrendingChain",
    "TopicFeedQuery",
    "TopicFeedResponse",
    # Moderation
    "ReportCreate",
    "ReportResponse",
    "BlockResponse",
    # Export
    "ExportCreate",
    "ExportResponse",
    # Upload
    "UploadRequest",
    "UploadResponse",
]
