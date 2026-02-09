"""Tests for uploads API endpoints."""

import pytest
from httpx import AsyncClient


class TestCreateUpload:
    """Tests for POST /api/v1/uploads"""

    @pytest.mark.asyncio
    async def test_create_upload_session(self, client: AsyncClient, auth_headers):
        """Test creating an upload session for a valid image returns 200."""
        response = await client.post(
            "/api/v1/uploads",
            headers=auth_headers,
            json={
                "filename": "screenshot.png",
                "content_type": "image/png",
                "size_bytes": 1024000,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "upload_id" in data
        assert "upload_url" in data
        assert "content_uri" in data

    @pytest.mark.asyncio
    async def test_upload_invalid_content_type(self, client: AsyncClient, auth_headers):
        """Test uploading with invalid content type returns 400."""
        response = await client.post(
            "/api/v1/uploads",
            headers=auth_headers,
            json={
                "filename": "malware.exe",
                "content_type": "application/x-executable",
                "size_bytes": 1024,
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"]["error"]["code"] == "INVALID_CONTENT_TYPE"

    @pytest.mark.asyncio
    async def test_upload_file_too_large(self, client: AsyncClient, auth_headers):
        """Test uploading a file that exceeds size limit returns 400."""
        response = await client.post(
            "/api/v1/uploads",
            headers=auth_headers,
            json={
                "filename": "huge_image.png",
                "content_type": "image/png",
                "size_bytes": 500 * 1024 * 1024,  # 500 MB, exceeds limit
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"]["error"]["code"] == "FILE_TOO_LARGE"

    @pytest.mark.asyncio
    async def test_upload_requires_auth(self, client: AsyncClient):
        """Test creating an upload session without authentication returns 401."""
        response = await client.post(
            "/api/v1/uploads",
            json={
                "filename": "screenshot.png",
                "content_type": "image/png",
                "size_bytes": 1024,
            },
        )

        assert response.status_code == 401
