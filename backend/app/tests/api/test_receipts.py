"""Tests for receipts API endpoints."""

import pytest
from httpx import AsyncClient


class TestCreateReceipt:
    """Tests for POST /api/v1/receipts"""
    
    @pytest.mark.asyncio
    async def test_create_receipt_success(self, client: AsyncClient, auth_headers):
        """Test successful receipt creation."""
        response = await client.post(
            "/api/v1/receipts",
            headers=auth_headers,
            json={
                "claim_text": "This is a test claim",
                "claim_type": "text",
                "implication_text": "This matters because...",
                "evidence": [
                    {
                        "type": "image",
                        "content_uri": "uploads/test/screenshot.png",
                        "caption": "Screenshot evidence",
                    }
                ],
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["claim_text"] == "This is a test claim"
        assert len(data["evidence"]) == 1
        assert data["evidence"][0]["type"] == "image"
    
    @pytest.mark.asyncio
    async def test_create_receipt_no_evidence(self, client: AsyncClient, auth_headers):
        """Test receipt creation fails without evidence."""
        response = await client.post(
            "/api/v1/receipts",
            headers=auth_headers,
            json={
                "claim_text": "This is a test claim",
                "evidence": [],  # Empty evidence
            },
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_receipt_unauthenticated(self, client: AsyncClient):
        """Test receipt creation requires auth."""
        response = await client.post(
            "/api/v1/receipts",
            json={
                "claim_text": "This is a test claim",
                "evidence": [
                    {
                        "type": "image",
                        "content_uri": "uploads/test/screenshot.png",
                    }
                ],
            },
        )
        
        assert response.status_code == 401


class TestGetReceipt:
    """Tests for GET /api/v1/receipts/{id}"""
    
    @pytest.mark.asyncio
    async def test_get_receipt_success(self, client: AsyncClient, auth_headers):
        """Test getting a receipt by ID."""
        # First create a receipt
        create_response = await client.post(
            "/api/v1/receipts",
            headers=auth_headers,
            json={
                "claim_text": "Test claim for get",
                "evidence": [
                    {
                        "type": "link",
                        "content_uri": "https://example.com/proof",
                    }
                ],
            },
        )
        receipt_id = create_response.json()["id"]
        
        # Now get it
        response = await client.get(f"/api/v1/receipts/{receipt_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == receipt_id
        assert data["claim_text"] == "Test claim for get"
    
    @pytest.mark.asyncio
    async def test_get_receipt_not_found(self, client: AsyncClient):
        """Test getting nonexistent receipt."""
        response = await client.get("/api/v1/receipts/nonexistent-id")
        
        assert response.status_code == 404
        assert response.json()["detail"]["error"]["code"] == "NOT_FOUND"


class TestForkReceipt:
    """Tests for POST /api/v1/receipts/{id}/fork"""
    
    @pytest.mark.asyncio
    async def test_fork_receipt_success(self, client: AsyncClient, auth_headers):
        """Test forking a receipt."""
        # Create original receipt
        create_response = await client.post(
            "/api/v1/receipts",
            headers=auth_headers,
            json={
                "claim_text": "Original claim",
                "evidence": [
                    {
                        "type": "image",
                        "content_uri": "uploads/test/original.png",
                    }
                ],
            },
        )
        original_id = create_response.json()["id"]
        
        # Fork it
        fork_response = await client.post(
            f"/api/v1/receipts/{original_id}/fork",
            headers=auth_headers,
            json={
                "claim_text": "Counter claim with evidence",
                "implication_text": "The original is wrong because...",
                "evidence": [
                    {
                        "type": "link",
                        "content_uri": "https://example.com/counter-proof",
                    }
                ],
            },
        )
        
        assert fork_response.status_code == 201
        fork_data = fork_response.json()
        
        assert fork_data["parent_receipt_id"] == original_id
        assert fork_data["claim_text"] == "Counter claim with evidence"
    
    @pytest.mark.asyncio
    async def test_fork_nonexistent_receipt(self, client: AsyncClient, auth_headers):
        """Test forking nonexistent receipt."""
        response = await client.post(
            "/api/v1/receipts/nonexistent-id/fork",
            headers=auth_headers,
            json={
                "claim_text": "Counter claim",
                "evidence": [
                    {
                        "type": "image",
                        "content_uri": "uploads/test/evidence.png",
                    }
                ],
            },
        )
        
        assert response.status_code == 404


class TestDeleteReceipt:
    """Tests for DELETE /api/v1/receipts/{id}"""
    
    @pytest.mark.asyncio
    async def test_delete_own_receipt(self, client: AsyncClient, auth_headers):
        """Test deleting own receipt."""
        # Create receipt
        create_response = await client.post(
            "/api/v1/receipts",
            headers=auth_headers,
            json={
                "claim_text": "To be deleted",
                "evidence": [
                    {
                        "type": "quote",
                        "content_uri": "Some quoted text",
                        "source_url": "https://example.com",
                    }
                ],
            },
        )
        receipt_id = create_response.json()["id"]
        
        # Delete it
        delete_response = await client.delete(
            f"/api/v1/receipts/{receipt_id}",
            headers=auth_headers,
        )
        
        assert delete_response.status_code == 204
        
        # Verify it's gone
        get_response = await client.get(f"/api/v1/receipts/{receipt_id}")
        assert get_response.status_code == 404


class TestReceiptChain:
    """Tests for GET /api/v1/receipts/{id}/chain"""
    
    @pytest.mark.asyncio
    async def test_get_chain(self, client: AsyncClient, auth_headers):
        """Test getting receipt chain."""
        # Create original
        original = await client.post(
            "/api/v1/receipts",
            headers=auth_headers,
            json={
                "claim_text": "Root claim",
                "evidence": [{"type": "link", "content_uri": "https://example.com"}],
            },
        )
        original_id = original.json()["id"]
        
        # Create fork
        await client.post(
            f"/api/v1/receipts/{original_id}/fork",
            headers=auth_headers,
            json={
                "claim_text": "Fork claim",
                "evidence": [{"type": "link", "content_uri": "https://counter.com"}],
            },
        )
        
        # Get chain
        chain_response = await client.get(f"/api/v1/receipts/{original_id}/chain")
        
        assert chain_response.status_code == 200
        chain = chain_response.json()
        
        assert chain["root"]["id"] == original_id
        assert chain["total_in_chain"] >= 2
