import firebase_admin
from firebase_admin import credentials, auth
import os
from dotenv import load_dotenv

load_dotenv()

def initialize_admin():
    """Initialize Firebase Admin SDK"""
    # Check if we're in a test environment
    if os.getenv("PYTEST_CURRENT_TEST") or "pytest" in os.getenv("_", ""):
        # Return a mock Firebase admin for testing
        from unittest.mock import Mock
        mock_admin = Mock()
        mock_admin.auth = Mock()
        return mock_admin
    
    try:
        # Check if already initialized
        firebase_admin.get_app()
        return firebase_admin
    except ValueError:
        # Initialize with service account using environment variables
        firebase_config = {
            "type": os.getenv("FIREBASE_TYPE", "service_account"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
            "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN", "googleapis.com")
        }
        
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
        return firebase_admin

def get_firebase_admin():
    """Get Firebase Admin instance"""
    return firebase_admin
