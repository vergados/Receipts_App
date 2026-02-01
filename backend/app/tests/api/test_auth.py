"""Tests for authentication API endpoints."""

import pytest
from httpx import AsyncClient


class TestAuthRegister:
    """Tests for POST /api/v1/auth/register"""
    
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123",
                "handle": "newuser",
                "display_name": "New User",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["handle"] == "newuser"
        
        assert "tokens" in data
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]
    
    @pytest.mark.asyncio
    async def test_register_invalid_password(self, client: AsyncClient):
        """Test registration with invalid password."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "weak",  # Too short, no uppercase, no number
                "handle": "user",
                "display_name": "User",
            },
        )
        
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registration with existing email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",  # Same as test_user
                "password": "SecurePass123",
                "handle": "anotheruser",
                "display_name": "Another User",
            },
        )
        
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "EMAIL_EXISTS"
    
    @pytest.mark.asyncio
    async def test_register_duplicate_handle(self, client: AsyncClient, test_user):
        """Test registration with existing handle."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "different@example.com",
                "password": "SecurePass123",
                "handle": "testuser",  # Same as test_user
                "display_name": "Different User",
            },
        )
        
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "HANDLE_EXISTS"


class TestAuthLogin:
    """Tests for POST /api/v1/auth/login"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPass123",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"
        
        assert "tokens" in data
        assert "access_token" in data["tokens"]
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Test login with wrong password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword123",
            },
        )
        
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent email."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePass123",
            },
        )
        
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


class TestAuthMe:
    """Tests for GET /api/v1/auth/me"""
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, auth_headers):
        """Test getting current authenticated user."""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == "test@example.com"
        assert data["handle"] == "testuser"
    
    @pytest.mark.asyncio
    async def test_get_current_user_unauthenticated(self, client: AsyncClient):
        """Test getting current user without auth."""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401


class TestAuthRefresh:
    """Tests for POST /api/v1/auth/refresh"""
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient, test_user):
        """Test refreshing access token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": test_user["refresh_token"]},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "Bearer"
    
    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client: AsyncClient):
        """Test refresh with invalid token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )
        
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_TOKEN"
