"""Tests for admin API endpoints."""

import pytest
from httpx import AsyncClient


class TestAdminStats:
    """Tests for GET /api/v1/admin/stats"""

    @pytest.mark.asyncio
    async def test_get_admin_stats(self, client: AsyncClient, mod_headers):
        """Test getting admin stats as a moderator returns 200."""
        response = await client.get(
            "/api/v1/admin/stats",
            headers=mod_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_receipts" in data
        assert "pending_reports" in data
        assert "total_reports" in data
        assert "actions_today" in data

    @pytest.mark.asyncio
    async def test_admin_requires_moderator(self, client: AsyncClient, auth_headers):
        """Test accessing admin stats as a regular user returns 403."""
        response = await client.get(
            "/api/v1/admin/stats",
            headers=auth_headers,
        )

        assert response.status_code == 403


class TestAdminReports:
    """Tests for GET /api/v1/admin/reports"""

    @pytest.mark.asyncio
    async def test_get_reports(self, client: AsyncClient, mod_headers):
        """Test getting admin reports as a moderator returns 200."""
        response = await client.get(
            "/api/v1/admin/reports",
            headers=mod_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "reports" in data
        assert "total" in data
        assert "pending_count" in data


class TestAdminUsers:
    """Tests for GET /api/v1/admin/users"""

    @pytest.mark.asyncio
    async def test_get_users(self, client: AsyncClient, mod_headers):
        """Test getting admin user list as a moderator returns 200."""
        response = await client.get(
            "/api/v1/admin/users",
            headers=mod_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data


class TestAdminActions:
    """Tests for GET /api/v1/admin/actions"""

    @pytest.mark.asyncio
    async def test_get_actions(self, client: AsyncClient, mod_headers):
        """Test getting moderation actions as a moderator returns 200."""
        response = await client.get(
            "/api/v1/admin/actions",
            headers=mod_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "actions" in data
        assert "total" in data
