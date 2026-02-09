"""Tests for reactions API endpoints."""

import pytest
from httpx import AsyncClient


class TestAddReaction:
    """Tests for POST /api/v1/receipts/{id}/reactions"""

    @pytest.mark.asyncio
    async def test_add_support_reaction(self, client: AsyncClient, auth_headers):
        """Test adding a support reaction to a receipt."""
        # Create a receipt first
        create_response = await client.post(
            "/api/v1/receipts",
            headers=auth_headers,
            json={
                "claim_text": "Claim for support reaction",
                "evidence": [
                    {
                        "type": "link",
                        "content_uri": "https://example.com/proof",
                    }
                ],
            },
        )
        receipt_id = create_response.json()["id"]

        # Add support reaction
        response = await client.post(
            f"/api/v1/receipts/{receipt_id}/reactions",
            headers=auth_headers,
            json={"type": "support"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["receipt_id"] == receipt_id
        assert data["type"] == "support"

    @pytest.mark.asyncio
    async def test_add_dispute_reaction(self, client: AsyncClient, auth_headers):
        """Test adding a dispute reaction to a receipt."""
        # Create a receipt first
        create_response = await client.post(
            "/api/v1/receipts",
            headers=auth_headers,
            json={
                "claim_text": "Claim for dispute reaction",
                "evidence": [
                    {
                        "type": "link",
                        "content_uri": "https://example.com/proof",
                    }
                ],
            },
        )
        receipt_id = create_response.json()["id"]

        # Add dispute reaction
        response = await client.post(
            f"/api/v1/receipts/{receipt_id}/reactions",
            headers=auth_headers,
            json={"type": "dispute"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["receipt_id"] == receipt_id
        assert data["type"] == "dispute"

    @pytest.mark.asyncio
    async def test_reaction_on_nonexistent_receipt(self, client: AsyncClient, auth_headers):
        """Test adding a reaction to a nonexistent receipt returns 404."""
        response = await client.post(
            "/api/v1/receipts/nonexistent-id/reactions",
            headers=auth_headers,
            json={"type": "support"},
        )

        assert response.status_code == 404
        assert response.json()["detail"]["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_reaction_requires_auth(self, client: AsyncClient):
        """Test adding a reaction without authentication returns 401."""
        response = await client.post(
            "/api/v1/receipts/some-id/reactions",
            json={"type": "support"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_duplicate_reaction_idempotent(self, client: AsyncClient, auth_headers):
        """Test adding the same reaction twice is handled gracefully."""
        # Create a receipt first
        create_response = await client.post(
            "/api/v1/receipts",
            headers=auth_headers,
            json={
                "claim_text": "Claim for duplicate reaction",
                "evidence": [
                    {
                        "type": "link",
                        "content_uri": "https://example.com/proof",
                    }
                ],
            },
        )
        receipt_id = create_response.json()["id"]

        # Add reaction first time
        first_response = await client.post(
            f"/api/v1/receipts/{receipt_id}/reactions",
            headers=auth_headers,
            json={"type": "support"},
        )
        assert first_response.status_code == 201

        # Add same reaction again - should return 201 or 409
        second_response = await client.post(
            f"/api/v1/receipts/{receipt_id}/reactions",
            headers=auth_headers,
            json={"type": "support"},
        )
        assert second_response.status_code in (201, 409)


class TestRemoveReaction:
    """Tests for DELETE /api/v1/receipts/{id}/reactions"""

    @pytest.mark.asyncio
    async def test_remove_reaction(self, client: AsyncClient, auth_headers):
        """Test removing a reaction from a receipt."""
        # Create a receipt first
        create_response = await client.post(
            "/api/v1/receipts",
            headers=auth_headers,
            json={
                "claim_text": "Claim for remove reaction",
                "evidence": [
                    {
                        "type": "link",
                        "content_uri": "https://example.com/proof",
                    }
                ],
            },
        )
        receipt_id = create_response.json()["id"]

        # Add reaction
        await client.post(
            f"/api/v1/receipts/{receipt_id}/reactions",
            headers=auth_headers,
            json={"type": "support"},
        )

        # Remove reaction
        response = await client.delete(
            f"/api/v1/receipts/{receipt_id}/reactions",
            headers=auth_headers,
            params={"type": "support"},
        )

        assert response.status_code == 204
