"""Tests for topics API endpoints."""

import pytest
from httpx import AsyncClient


class TestListTopics:
    """Tests for GET /api/v1/topics"""

    @pytest.mark.asyncio
    async def test_list_topics_empty(self, client: AsyncClient):
        """Test listing topics when none exist returns 200 with empty list."""
        response = await client.get("/api/v1/topics")

        assert response.status_code == 200
        data = response.json()
        assert "topics" in data
        assert data["topics"] == []

    @pytest.mark.asyncio
    async def test_list_topics(self, client: AsyncClient, test_topic):
        """Test listing topics includes the test topic."""
        response = await client.get("/api/v1/topics")

        assert response.status_code == 200
        data = response.json()
        assert len(data["topics"]) >= 1

        slugs = [t["slug"] for t in data["topics"]]
        assert "test-topic" in slugs


class TestGetTopic:
    """Tests for GET /api/v1/topics/{slug}"""

    @pytest.mark.asyncio
    async def test_get_topic_by_slug(self, client: AsyncClient, test_topic):
        """Test getting a topic by its slug returns 200 with correct data."""
        response = await client.get(f"/api/v1/topics/{test_topic.slug}")

        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "test-topic"
        assert data["name"] == "Test Topic"

    @pytest.mark.asyncio
    async def test_get_topic_not_found(self, client: AsyncClient):
        """Test getting a nonexistent topic returns 404."""
        response = await client.get("/api/v1/topics/nonexistent-slug")

        assert response.status_code == 404
        assert response.json()["detail"]["error"]["code"] == "NOT_FOUND"
