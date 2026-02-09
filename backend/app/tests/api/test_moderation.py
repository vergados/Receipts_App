"""Tests for moderation API endpoints."""

import pytest
from httpx import AsyncClient


class TestCreateReport:
    """Tests for POST /api/v1/reports"""

    @pytest.mark.asyncio
    async def test_create_report(self, client: AsyncClient, auth_headers):
        """Test creating a report on a receipt returns 201."""
        # Create a receipt to report
        create_response = await client.post(
            "/api/v1/receipts",
            headers=auth_headers,
            json={
                "claim_text": "Claim to be reported",
                "evidence": [
                    {
                        "type": "link",
                        "content_uri": "https://example.com/proof",
                    }
                ],
            },
        )
        receipt_id = create_response.json()["id"]

        # Report the receipt
        response = await client.post(
            "/api/v1/reports",
            headers=auth_headers,
            json={
                "target_type": "receipt",
                "target_id": receipt_id,
                "reason": "spam",
                "details": "This is spam content",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["target_type"] == "receipt"
        assert data["target_id"] == receipt_id
        assert data["reason"] == "spam"
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_create_report_unauthenticated(self, client: AsyncClient):
        """Test creating a report without authentication returns 401."""
        response = await client.post(
            "/api/v1/reports",
            json={
                "target_type": "receipt",
                "target_id": "some-id",
                "reason": "spam",
            },
        )

        assert response.status_code == 401


class TestBlockUser:
    """Tests for POST/DELETE /api/v1/users/{id}/block"""

    @pytest.mark.asyncio
    async def test_block_user(self, client: AsyncClient, auth_headers, test_user_2):
        """Test blocking another user returns 201."""
        user2_id = test_user_2["user"].id

        response = await client.post(
            f"/api/v1/users/{user2_id}/block",
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["blocked_user_id"] == user2_id

    @pytest.mark.asyncio
    async def test_unblock_user(self, client: AsyncClient, auth_headers, test_user_2):
        """Test unblocking a previously blocked user returns 204."""
        user2_id = test_user_2["user"].id

        # Block user first
        await client.post(
            f"/api/v1/users/{user2_id}/block",
            headers=auth_headers,
        )

        # Unblock user
        response = await client.delete(
            f"/api/v1/users/{user2_id}/block",
            headers=auth_headers,
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_block_nonexistent_user(self, client: AsyncClient, auth_headers):
        """Test blocking a nonexistent user returns 404."""
        response = await client.post(
            "/api/v1/users/nonexistent-user-id/block",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["detail"]["error"]["code"] == "NOT_FOUND"
