"""Tests for exports API endpoints."""

import pytest
from httpx import AsyncClient


class TestCreateExport:
    """Tests for POST /api/v1/receipts/{id}/export"""

    @pytest.mark.asyncio
    async def test_create_export(self, client: AsyncClient, auth_headers):
        """Test creating an export for a receipt returns 202."""
        # Create a receipt first
        create_response = await client.post(
            "/api/v1/receipts",
            headers=auth_headers,
            json={
                "claim_text": "Claim for export test",
                "evidence": [
                    {
                        "type": "link",
                        "content_uri": "https://example.com/proof",
                    }
                ],
            },
        )
        receipt_id = create_response.json()["id"]

        # Export the receipt
        response = await client.post(
            f"/api/v1/receipts/{receipt_id}/export",
            headers=auth_headers,
            json={
                "format": "image",
                "include_evidence_thumbnails": True,
                "include_chain_preview": False,
            },
        )

        assert response.status_code == 202
        data = response.json()
        assert "export_id" in data
        assert data["format"] == "image"

    @pytest.mark.asyncio
    async def test_create_export_nonexistent_receipt(self, client: AsyncClient, auth_headers):
        """Test creating an export for a nonexistent receipt returns 404."""
        response = await client.post(
            "/api/v1/receipts/nonexistent-id/export",
            headers=auth_headers,
            json={
                "format": "image",
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"]["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_create_export_requires_auth(self, client: AsyncClient):
        """Test creating an export without authentication returns 401."""
        response = await client.post(
            "/api/v1/receipts/some-id/export",
            json={
                "format": "image",
            },
        )

        assert response.status_code == 401


class TestGetExport:
    """Tests for GET /api/v1/exports/{id}"""

    @pytest.mark.asyncio
    async def test_get_export_not_found(self, client: AsyncClient, auth_headers):
        """Test getting a nonexistent export returns 404."""
        response = await client.get(
            "/api/v1/exports/nonexistent-export-id",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["detail"]["error"]["code"] == "NOT_FOUND"
