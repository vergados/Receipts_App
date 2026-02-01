"""Topics API endpoints - SYNC version."""

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import DbSession
from app.models.schemas.topic import TopicListResponse, TopicResponse
from app.services.topic_service import TopicService

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("", response_model=TopicListResponse)
def list_topics(db: DbSession) -> TopicListResponse:
    """List all topics."""
    service = TopicService(db)
    topics = service.get_all()

    topic_responses = []
    for topic in topics:
        receipt_count = service.get_receipt_count(topic.id)
        topic_responses.append(service.topic_to_response(topic, receipt_count))

    return TopicListResponse(topics=topic_responses)


@router.get("/{slug}", response_model=TopicResponse)
def get_topic(slug: str, db: DbSession) -> TopicResponse:
    """Get topic by slug."""
    service = TopicService(db)
    topic = service.get_by_slug(slug)

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Topic '{slug}' not found",
                }
            },
        )

    receipt_count = service.get_receipt_count(topic.id)
    return service.topic_to_response(topic, receipt_count)
