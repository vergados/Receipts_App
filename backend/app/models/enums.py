"""Enumeration types used throughout the application."""

from enum import Enum


class ClaimType(str, Enum):
    """Type of claim in a receipt."""
    
    TEXT = "text"
    VIDEO_TRANSCRIPT = "video_transcript"


class EvidenceType(str, Enum):
    """Type of evidence attached to a receipt."""
    
    IMAGE = "image"
    LINK = "link"
    VIDEO = "video"
    QUOTE = "quote"


class Visibility(str, Enum):
    """Visibility setting for content."""
    
    PUBLIC = "public"
    UNLISTED = "unlisted"


class ReactionType(str, Enum):
    """Type of reaction to a receipt."""
    
    SUPPORT = "support"
    DISPUTE = "dispute"
    BOOKMARK = "bookmark"


class ReportReason(str, Enum):
    """Reason for reporting content."""
    
    DOXXING = "doxxing"
    HARASSMENT = "harassment"
    SPAM = "spam"
    MISINFORMATION = "misinformation"
    OTHER = "other"


class ReportStatus(str, Enum):
    """Status of a report."""
    
    PENDING = "pending"
    REVIEWED = "reviewed"
    ACTIONED = "actioned"
    DISMISSED = "dismissed"


class TargetType(str, Enum):
    """Type of target for reports and moderation actions."""
    
    RECEIPT = "receipt"
    USER = "user"


class ModerationActionType(str, Enum):
    """Type of moderation action taken."""
    
    WARNING = "warning"
    CONTENT_REMOVAL = "content_removal"
    USER_BAN = "user_ban"
    USER_SUSPENSION = "user_suspension"


class ExportStatus(str, Enum):
    """Status of an export job."""
    
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExportFormat(str, Enum):
    """Format for exported receipt cards."""

    IMAGE = "image"
    # VIDEO = "video"  # v2


class NotificationType(str, Enum):
    """Type of notification."""

    RECEIPT_SUPPORT = "receipt_support"  # Someone supported your receipt
    RECEIPT_DISPUTE = "receipt_dispute"  # Someone disputed your receipt
    RECEIPT_COUNTER = "receipt_counter"  # Someone countered your receipt
    RECEIPT_BOOKMARK = "receipt_bookmark"  # Someone bookmarked your receipt
    NEW_FOLLOWER = "new_follower"  # Someone followed you (future)
    MENTION = "mention"  # Someone mentioned you (future)


class OrganizationRole(str, Enum):
    """Role within a newsroom organization."""

    ADMIN = "admin"  # Full control over organization
    EDITOR = "editor"  # Review and publish content
    SENIOR_REPORTER = "senior_reporter"  # Direct publish capability
    REPORTER = "reporter"  # Needs approval
    CONTRIBUTOR = "contributor"  # Limited access
