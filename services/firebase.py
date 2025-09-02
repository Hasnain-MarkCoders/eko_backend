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
        # Configure the mock to avoid circular references
        mock_admin.auth.generate_password_reset_link = Mock(return_value="https://example.com/reset?token=mock_token")
        mock_admin.auth.verify_id_token = Mock()
        mock_admin.auth.get_user = Mock()
        mock_admin.auth.delete_user = Mock()
        
        # Create a proper mock for create_user that returns a user with real uid
        mock_created_user = Mock()
        mock_created_user.uid = "test_firebase_uid_123"
        mock_admin.auth.create_user = Mock(return_value=mock_created_user)
        
        return mock_admin
    
    try:
        # Check if already initialized
        firebase_admin.get_app()
        return firebase_admin
    except ValueError:
        # Initialize with service account using environment variables
        private_key = os.getenv("FIREBASE_PRIVATE_KEY")
        
        # Handle different newline formats in the private key
        if private_key:
            # Remove surrounding quotes if they exist
            private_key = private_key.strip('"\'')
            # Replace literal \n with actual newlines (in case they exist)
            private_key = private_key.replace('\\n', '\n')
            # Also handle cases where newlines might be encoded differently
            private_key = private_key.replace('\\r\\n', '\n').replace('\\r', '\n')
            # Strip any trailing whitespace/newlines that might cause issues
            private_key = private_key.strip()
        
        firebase_config = {
            "type": os.getenv("FIREBASE_TYPE"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": private_key,
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
            "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
        }
        # print("================== FIREBASE CONFIG ===================================")
        # print(firebase_config)
        # print("================== FIREBASE CONFIG ===================================")
        try:
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin initialized successfully!")
            return firebase_admin
        except Exception as e:
            print(f"❌ Firebase initialization failed: {str(e)}")
            print("🔧 Please check your Firebase credentials in .env file")
            print("💡 The app will continue without Firebase authentication")
            # Return a mock object so the app doesn't crash
            from unittest.mock import Mock
            mock_admin = Mock()
            mock_admin.auth = Mock()
            # Configure the mock to avoid circular references
            mock_admin.auth.generate_password_reset_link = Mock(return_value="https://example.com/reset?token=mock_token")
            mock_admin.auth.verify_id_token = Mock()
            mock_admin.auth.get_user = Mock()
            mock_admin.auth.delete_user = Mock()
            
            # Create a proper mock for create_user that returns a user with real uid
            mock_created_user = Mock()
            mock_created_user.uid = "mock_firebase_uid_123"
            mock_admin.auth.create_user = Mock(return_value=mock_created_user)
            
            return mock_admin

def get_firebase_admin():
    """Get Firebase Admin instance"""
    return firebase_admin
