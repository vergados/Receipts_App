"""Tests for notifications API endpoints."""

import pytest
from httpx import AsyncClient


class TestGetNotifications:
    """Tests for GET /api/v1/notifications"""

    @pytest.mark.asyncio
    async def test_get_notifications_empty(self, client: AsyncClient, auth_headers):
        """Test getting notifications when none exist returns 200 with empty list."""
        response = await client.get(
            "/api/v1/notifications",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert data["notifications"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_get_notifications_requires_auth(self, client: AsyncClient):
        """Test getting notifications without authentication returns 401."""
        response = await client.get("/api/v1/notifications")

        assert response.status_code == 401


class TestUnreadCount:
    """Tests for GET /api/v1/notifications/unread-count"""

    @pytest.mark.asyncio
    async def test_get_unread_count(self, client: AsyncClient, auth_headers):
        """Test getting unread notification count returns 200 with count field."""
        response = await client.get(
            "/api/v1/notifications/unread-count",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "unread_count" in data
        assert data["unread_count"] == 0


class TestMarkRead:
    """Tests for POST /api/v1/notifications/mark-read"""

    @pytest.mark.asyncio
    async def test_mark_read(self, client: AsyncClient, auth_headers):
        """Test marking notifications as read returns 200."""
        response = await client.post(
            "/api/v1/notifications/mark-read",
            headers=auth_headers,
            json={"notification_ids": []},
        )

        assert response.status_code == 200
        data = response.json()
        assert "marked_count" in data


class TestDeleteNotifications:
    """Tests for DELETE /api/v1/notifications"""

    @pytest.mark.asyncio
    async def test_delete_all_notifications(self, client: AsyncClient, auth_headers):
        """Test deleting all notifications returns 200 with deleted count."""
        response = await client.delete(
            "/api/v1/notifications",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "deleted_count" in data
        assert data["deleted_count"] == 0
