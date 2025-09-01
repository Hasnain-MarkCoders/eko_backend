import firebase_admin
from firebase_admin import credentials, auth
import os
from dotenv import load_dotenv

load_dotenv()

def initialize_admin():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if already initialized
        firebase_admin.get_app()
        return firebase_admin
    except ValueError:
        # Initialize with service account
        cred = credentials.Certificate("proj-eko-firebase-adminsdk-fbsvc-ef603323dd.json")
        firebase_admin.initialize_app(cred)
        return firebase_admin

def get_firebase_admin():
    """Get Firebase Admin instance"""
    return firebase_admin 