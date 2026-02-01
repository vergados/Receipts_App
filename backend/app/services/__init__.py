"""Services package - business logic layer."""

from app.services.auth_service import AuthService, AuthServiceError, InvalidRefreshTokenError
from app.services.export_service import ExportService, ExportServiceError
from app.services.feed_service import FeedService
from app.services.media_service import (
    FileTooLargeError,
    InvalidContentTypeError,
    MediaService,
    MediaServiceError,
)
from app.services.moderation_service import (
    AlreadyReportedError,
    ModerationService,
    ModerationServiceError,
)
from app.services.reaction_service import ReactionService, ReactionServiceError
from app.services.receipt_service import (
    EvidenceRequiredError,
    NotAuthorizedError,
    ReceiptNotFoundError,
    ReceiptService,
    ReceiptServiceError,
)
from app.services.topic_service import (
    TopicAlreadyExistsError,
    TopicNotFoundError,
    TopicService,
    TopicServiceError,
)
from app.services.user_service import (
    EmailAlreadyExistsError,
    HandleAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
    UserService,
    UserServiceError,
)

__all__ = [
    # User service
    "UserService",
    "UserServiceError",
    "EmailAlreadyExistsError",
    "HandleAlreadyExistsError",
    "UserNotFoundError",
    "InvalidCredentialsError",
    # Auth service
    "AuthService",
    "AuthServiceError",
    "InvalidRefreshTokenError",
    # Receipt service
    "ReceiptService",
    "ReceiptServiceError",
    "ReceiptNotFoundError",
    "NotAuthorizedError",
    "EvidenceRequiredError",
    # Topic service
    "TopicService",
    "TopicServiceError",
    "TopicNotFoundError",
    "TopicAlreadyExistsError",
    # Feed service
    "FeedService",
    # Reaction service
    "ReactionService",
    "ReactionServiceError",
    # Moderation service
    "ModerationService",
    "ModerationServiceError",
    "AlreadyReportedError",
    # Export service
    "ExportService",
    "ExportServiceError",
    # Media service
    "MediaService",
    "MediaServiceError",
    "InvalidContentTypeError",
    "FileTooLargeError",
]
