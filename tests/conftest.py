import pytest
import asyncio
from fastapi.testclient import TestClient
from bson import ObjectId
import jwt
import os
from dotenv import load_dotenv

# Load test environment
load_dotenv()

# Test JWT secret - use the same key as the middleware
TEST_TOKEN_KEY = os.getenv("TOKEN_KEY", "Test_124")

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_user():
    """Create a test user fixture."""
    return {
        "_id": str(ObjectId()),
        "uid": "test_uid_123",
        "email": "test@example.com",
        "name": "Test User",
        "provider": "email",
        "status": "active",
        "welcome": True,
        "image": "https://example.com/test.jpg",
        "type": "user",
        "notificationToken": "",
        "isDeleted": False
    }

@pytest.fixture
def test_token(test_user):
    """Generate a test JWT token."""
    return jwt.encode({"_id": test_user["_id"]}, TEST_TOKEN_KEY, algorithm="HS256")

@pytest.fixture
def auth_headers(test_token):
    """Return headers with authentication token."""
    return {"Authorization": f"Bearer {test_token}"}

@pytest.fixture
def client(test_user):
    """Create test client with mocked authentication."""
    from app import app
    from middleware.auth import get_current_user
    
    # Override the get_current_user dependency for all tests
    async def mock_get_current_user():
        return test_user
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up dependency overrides
    app.dependency_overrides.clear() 