"""Tests for users API endpoints."""

import pytest
from httpx import AsyncClient


class TestGetUserProfile:
    """Tests for GET /api/v1/users/{handle}"""

    @pytest.mark.asyncio
    async def test_get_user_profile(self, client: AsyncClient, test_user):
        """Test getting a user profile by handle returns 200."""
        response = await client.get("/api/v1/users/testuser")

        assert response.status_code == 200
        data = response.json()
        assert data["handle"] == "testuser"
        assert data["display_name"] == "Test User"

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client: AsyncClient):
        """Test getting a nonexistent user profile returns 404."""
        response = await client.get("/api/v1/users/nonexistenthandle")

        assert response.status_code == 404
        assert response.json()["detail"]["error"]["code"] == "NOT_FOUND"


class TestUpdateProfile:
    """Tests for PATCH /api/v1/users/me"""

    @pytest.mark.asyncio
    async def test_update_profile(self, client: AsyncClient, auth_headers):
        """Test updating the current user's display name returns 200."""
        response = await client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={
                "display_name": "Updated Display Name",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "Updated Display Name"
