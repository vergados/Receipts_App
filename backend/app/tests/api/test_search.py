"""Tests for search API endpoints."""

import pytest
from httpx import AsyncClient


class TestSearch:
    """Tests for GET /api/v1/search"""

    @pytest.mark.asyncio
    async def test_search_by_claim(self, client: AsyncClient, auth_headers):
        """Test searching receipts by claim text returns matching results."""
        # Create a receipt with a unique claim
        await client.post(
            "/api/v1/receipts",
            headers=auth_headers,
            json={
                "claim_text": "UniqueSearchableClaim12345",
                "evidence": [
                    {
                        "type": "link",
                        "content_uri": "https://example.com/proof",
                    }
                ],
            },
        )

        # Search for the unique claim
        response = await client.get(
            "/api/v1/search",
            params={"q": "UniqueSearchableClaim12345"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["receipts"]) >= 1
        assert "UniqueSearchableClaim12345" in data["receipts"][0]["claim_text"]

    @pytest.mark.asyncio
    async def test_search_no_results(self, client: AsyncClient):
        """Test searching with nonsense string returns empty results."""
        response = await client.get(
            "/api/v1/search",
            params={"q": "xyznonexistent999qqq"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["receipts"] == []

    @pytest.mark.asyncio
    async def test_search_empty_query(self, client: AsyncClient):
        """Test searching with empty query returns 422 validation error."""
        response = await client.get(
            "/api/v1/search",
            params={"q": ""},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_pagination(self, client: AsyncClient, auth_headers):
        """Test search pagination with limit parameter."""
        # Create two receipts with the same keyword
        for i in range(2):
            await client.post(
                "/api/v1/receipts",
                headers=auth_headers,
                json={
                    "claim_text": f"PaginationTestKeyword claim number {i}",
                    "evidence": [
                        {
                            "type": "link",
                            "content_uri": f"https://example.com/proof{i}",
                        }
                    ],
                },
            )

        # Search with limit=1
        response = await client.get(
            "/api/v1/search",
            params={"q": "PaginationTestKeyword", "limit": 1},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["receipts"]) == 1
        assert data["pagination"]["has_more"] is True
