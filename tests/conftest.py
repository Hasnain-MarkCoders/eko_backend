import pytest
import asyncio
from unittest.mock import patch, Mock, AsyncMock
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
def mock_database():
    """Mock database operations."""
    mock_users = AsyncMock()
    mock_users.find_one = AsyncMock()
    mock_users.update_one = AsyncMock()
    mock_users.insert_one = AsyncMock()
    mock_users.find = AsyncMock()
    
    # Default mock responses
    mock_users.find_one.return_value = {
        "_id": "68b616805a6658835e82fe8c",
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
    
    mock_users.update_one.return_value = Mock(modified_count=1)
    mock_users.insert_one.return_value = Mock(inserted_id="new_user_id")
    
    return mock_users

@pytest.fixture
def mock_firebase_auth():
    """Mock Firebase authentication."""
    mock_auth = Mock()
    mock_auth.verify_id_token = AsyncMock()
    mock_auth.get_user = AsyncMock()
    mock_auth.generate_password_reset_link = Mock()
    
    # Default mock user data
    mock_user_data = {
        "uid": "firebase_uid_123",
        "email": "test@example.com",
        "name": "Test User",
        "email_verified": True
    }
    
    mock_auth.verify_id_token.return_value = mock_user_data
    mock_auth.get_user.return_value = Mock(
        uid="firebase_uid_123",
        email="test@example.com",
        display_name="Test User"
    )
    # Mock password reset link generation
    mock_auth.generate_password_reset_link.return_value = "https://example.com/reset?token=mock_token"
    
    return mock_auth

@pytest.fixture
def client(test_user, mock_database, mock_firebase_auth):
    """Create test client with mocked dependencies."""
    # Patch the database module imports at the module level
    with patch('controllers.auth_controller.users', mock_database):
        with patch('controllers.profile_controller.users', mock_database):
            with patch('middleware.auth.users', mock_database):
                with patch('services.firebase.initialize_admin') as mock_firebase_init:
                    with patch('firebase_admin.auth', mock_firebase_auth):
                        # Mock Firebase admin initialization
                        mock_firebase_admin = Mock()
                        mock_firebase_admin.auth = mock_firebase_auth
                        mock_firebase_init.return_value = mock_firebase_admin
                        
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
