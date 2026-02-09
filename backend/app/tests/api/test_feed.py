"""Tests for feed API endpoints."""

import pytest
from httpx import AsyncClient


class TestGetFeed:
    """Tests for GET /api/v1/feed"""

    @pytest.mark.asyncio
    async def test_get_feed_empty(self, client: AsyncClient):
        """Test getting feed when no receipts exist returns 200 with empty list."""
        response = await client.get("/api/v1/feed")

        assert response.status_code == 200
        data = response.json()
        assert "receipts" in data
        assert data["receipts"] == []

    @pytest.mark.asyncio
    async def test_get_feed_with_receipts(self, client: AsyncClient, auth_headers):
        """Test getting feed after creating a receipt shows it in the feed."""
        # Create a receipt
        await client.post(
            "/api/v1/receipts",
            headers=auth_headers,
            json={
                "claim_text": "Feed test claim",
                "evidence": [
                    {
                        "type": "link",
                        "content_uri": "https://example.com/proof",
                    }
                ],
            },
        )

        # Get feed
        response = await client.get("/api/v1/feed")

        assert response.status_code == 200
        data = response.json()
        assert len(data["receipts"]) >= 1
        assert data["receipts"][0]["claim_text"] == "Feed test claim"


class TestGetTrending:
    """Tests for GET /api/v1/feed/trending"""

    @pytest.mark.asyncio
    async def test_get_trending(self, client: AsyncClient):
        """Test getting trending feed returns 200 with correct structure."""
        response = await client.get("/api/v1/feed/trending")

        assert response.status_code == 200
        data = response.json()
        assert "chains" in data


class TestGetTopicFeed:
    """Tests for GET /api/v1/feed/topic/{slug}"""

    @pytest.mark.asyncio
    async def test_get_topic_feed(self, client: AsyncClient, test_topic):
        """Test getting topic feed for an existing topic returns 200."""
        response = await client.get(f"/api/v1/feed/topic/{test_topic.slug}")

        assert response.status_code == 200
        data = response.json()
        assert "topic" in data
        assert "receipts" in data
        assert data["topic"]["slug"] == test_topic.slug

    @pytest.mark.asyncio
    async def test_get_topic_feed_not_found(self, client: AsyncClient):
        """Test getting topic feed for nonexistent topic returns 404."""
        response = await client.get("/api/v1/feed/topic/nonexistent-slug")

        assert response.status_code == 404
        assert response.json()["detail"]["error"]["code"] == "NOT_FOUND"
