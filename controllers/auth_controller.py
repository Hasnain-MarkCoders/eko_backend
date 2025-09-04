from fastapi import HTTPException, status
from database import users
from services.firebase import initialize_admin
import jwt
import os
from dotenv import load_dotenv
from bson import ObjectId
from datetime import datetime, timezone
from locales import get_message
from schemas.enums import Language, LanguageRequest

load_dotenv()

TOKEN_KEY = os.getenv("TOKEN_KEY", "Test_124")  # Default fallback
default_photo = "https://sauced-app-bucket.s3.us-east-2.amazonaws.com/sauced_placeholder.webp"

class AuthController:
    def __init__(self):
        self.admin = initialize_admin()
    
    async def email_password_signup(self, email: str, password: str, confirm_password: str, language: str, agreed: bool):
        """Email/password signup using Firebase - uses language from request body"""
        # Convert request language (en/fr) to database language (english/french)
        database_language = LanguageRequest.to_database_language(language)
        # Convert database language to locale code for get_message()
        locale_code = Language.get_locale_code(database_language)
        
        try:
            # Check if user already exists in database
            existing_user = await users.find_one({"email": email})
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(locale_code, "auth.signup.email_exists")
                )
            
            # Create user in Firebase
            user_properties = {
                "email": email,
                "password": password,
                "email_verified": False
            }
            
            firebase_user = self.admin.auth.create_user(**user_properties)
            uid = firebase_user.uid
            
            # Create user in database
            new_user = {
                "uid": uid,
                "email": email,
                "name": "",  # Empty name initially, will be set during onboarding
                "provider": "password",
                "status": "active",
                "welcome": True,
                "image": default_photo,
                "type": "user",
                "notificationToken": "",
                "isDeleted": False,
                "language": database_language,  # Store user's language preference (converted to database format)
                "createdAt": datetime.now(timezone.utc),
                "updatedAt": datetime.now(timezone.utc)
            }
            
            result = await users.insert_one(new_user)
            new_user["_id"] = str(result.inserted_id)
            
            # Generate JWT token
            token = jwt.encode({"_id": str(result.inserted_id)}, TOKEN_KEY, algorithm="HS256")
            
            return {
                "success": True,
                "message": get_message(locale_code, "auth.signup.success"),
                "data": {
                    "user_id": str(result.inserted_id),
                    "uid": new_user["uid"],
                    "email": new_user["email"],
                    "name": new_user["name"],
                    "provider": new_user["provider"],
                    "status": new_user["status"],
                    "welcome": new_user["welcome"],
                    "image": new_user["image"],
                    "type": new_user["type"],
                    "notificationToken": new_user["notificationToken"],
                    "isDeleted": new_user["isDeleted"],
                    "createdAt": new_user["createdAt"],
                    "updatedAt": new_user["updatedAt"],
                    "token": token
                }
            }
            
        except HTTPException:
            # Re-raise HTTPExceptions (like email already exists from MongoDB check)
            raise
        except Exception as error:
            print(f"ERROR = {error}")
            if "EMAIL_EXISTS" in str(error):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(locale_code, "auth.signup.email_exists")
                )
            elif "WEAK_PASSWORD" in str(error):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(locale_code, "auth.signup.weak_password")
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(locale_code, "general.internal_error")
                )
    
    async def email_password_login(self, email: str, password: str, language: str = "en"):
        """Email/password login using Firebase"""
        try:
            # Validate password is not empty
            if not password or password.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(language, "auth.login.invalid_credentials")
                )
            
            # Check if user exists in database
            existing_user = await users.find_one({"email": email})
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(language, "auth.login.user_not_found")
                )
            
            # Get user's stored language preference for error messages
            user_language = existing_user.get("language", "english")
            # Convert database language (english/french) to locale code (en/fr)
            if user_language == "french":
                user_locale = "fr"
            else:
                user_locale = "en"
            
            # Check if user is deleted
            if existing_user.get("isDeleted", False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(user_locale, "auth.login.account_deleted")
                )
            
            # Check if user is brand type
            if existing_user.get("type") == "brand":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(user_locale, "auth.login.brand_user")
                )
            
            # Verify password with Firebase using REST API
            firebase_api_key = os.getenv("FIREBASE_API_KEY")
            if not firebase_api_key:
                print("❌ FIREBASE_API_KEY not found - cannot verify password")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=get_message(user_locale, "general.internal_error")
                )
            
            try:
                import httpx
                url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_api_key}"
                payload = {
                    "email": email,
                    "password": password,
                    "returnSecureToken": True
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, json=payload)
                    
                    if response.status_code != 200:
                        # Firebase says password is wrong - DO NOT create token
                        print(f"❌ Firebase password verification failed for {email}")
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=get_message(user_locale, "auth.login.invalid_credentials")
                        )
                    
                    # Firebase says password is correct - NOW we can create token
                    firebase_response = response.json()
                    print(f"✅ Firebase authentication successful for {email}")
                    
            except HTTPException:
                raise
            except Exception as e:
                print(f"❌ Firebase password verification error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=get_message(user_locale, "auth.login.invalid_credentials")
                )
            
            # Convert ObjectId to string for serialization
            existing_user["_id"] = str(existing_user["_id"])
            
            # ONLY create JWT token after Firebase confirms password is correct
            token = jwt.encode({"_id": existing_user["_id"]}, TOKEN_KEY, algorithm="HS256")
            
            return {
                "success": True,
                "message": get_message(user_locale, "auth.login.success"),
                "data": {
                    "user_id": existing_user["_id"],
                    "uid": existing_user["uid"],
                    "email": existing_user["email"],
                    "name": existing_user["name"],
                    "provider": existing_user["provider"],
                    "status": existing_user["status"],
                    "welcome": existing_user["welcome"],
                    "image": existing_user["image"],
                    "type": existing_user["type"],
                    "notificationToken": existing_user["notificationToken"],
                    "isDeleted": existing_user["isDeleted"],
                    "createdAt": existing_user["createdAt"],
                    "updatedAt": existing_user["updatedAt"],
                    "token": token
                }
            }
            
        except HTTPException:
            # Re-raise HTTPExceptions (like user not found, account deleted, etc.)
            raise
        except Exception as error:
            print(f"ERROR = {error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_message(language, "general.internal_error")
            )
    
    async def forgot_password(self, email: str, language: str = "en"):
        """Send password reset email using Firebase"""
        try:
            # Check if user exists in database
            existing_user = await users.find_one({"email": email})
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(language, "auth.login.user_not_found")
                )
            
            # Check if user is deleted
            if existing_user.get("isDeleted", False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(language, "auth.login.account_deleted")
                )
            
            # Check if user is brand type
            if existing_user.get("type") == "brand":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(language, "auth.login.brand_user")
                )
            
            # Generate password reset link using Firebase
            try:
                reset_link = self.admin.auth.generate_password_reset_link(
                    email,
                    action_code_settings=None  # Use default settings
                )
                
                # In a real application, you would send this link via email
                # For now, we'll return the link (in production, send via email service)
                
                return {
                    "success": True,
                    "message": get_message(language, "auth.forgot_password.success"),
                    "data": {
                        "resetLink": reset_link,
                        "note": "In production, this link would be sent via email"
                    }
                }
                
            except Exception as firebase_error:
                print(f"Firebase password reset error: {firebase_error}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=get_message(language, "auth.forgot_password.reset_failed")
                )
            
        except Exception as error:
            print(f"ERROR = {error}")
            if isinstance(error, HTTPException):
                raise error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error)
            )
    
    async def onboarding(self, user_id: str, name: str, age: int, gender: str, language: str, purpose: str, user_language: str = "en"):
        """Complete user onboarding with additional profile information - uses user's stored language preference"""
        # Convert request language (en/fr) to database language (english/french)
        database_language = LanguageRequest.to_database_language(language)
        try:
            # Convert string user_id to ObjectId
            try:
                object_id = ObjectId(user_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(user_language, "general.invalid_user_id")
                )
            
            # Get current user
            current_user = await users.find_one({"_id": object_id})
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(language, "auth.login.user_not_found")
                )
            
            # Check if user has already been welcomed (onboarding completed)
            if not current_user.get("welcome", True):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(user_language, "auth.onboarding.already_completed")
                )
            
            # Check if user is deleted
            if current_user.get("isDeleted", False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(language, "auth.login.account_deleted")
                )
            
            # Update name in Firebase first (like profile/change-name API)
            firebase_uid = current_user.get("uid")
            if firebase_uid:
                try:
                    self.admin.auth.update_user(
                        firebase_uid,
                        display_name=name
                    )
                    print(f"✅ Firebase display name updated for user {firebase_uid}")
                except Exception as e:
                    print(f"❌ Firebase update error: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=get_message(user_language, "auth.onboarding.firebase_update_failed")
                    )
            
            # Update user in MongoDB with onboarding data
            update_data = {
                "name": name,
                "age": age,
                "gender": gender,
                "language": database_language,
                "purpose": purpose,
                "welcome": False,  # Set welcome to false after onboarding completion
                "updatedAt": datetime.now(timezone.utc)
            }
            
            result = await users.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(language, "auth.login.user_not_found")
                )
            
            # Get updated user
            updated_user = await users.find_one({"_id": object_id})
            updated_user["_id"] = str(updated_user["_id"])
            
            # Generate JWT token
            token = jwt.encode({"_id": str(updated_user["_id"])}, TOKEN_KEY, algorithm="HS256")
            
            return {
                "success": True,
                "message": get_message(user_language, "auth.onboarding.success"),
                "data": {
                    "user_id": str(updated_user["_id"]),
                    "name": updated_user.get("name"),
                    "email": updated_user.get("email"),
                    "age": updated_user.get("age"),
                    "gender": updated_user.get("gender"),
                    "language": updated_user.get("language"),
                    "purpose": updated_user.get("purpose"),
                    "welcome": updated_user.get("welcome", False),
                    "token": token
                }
            }
            
        except Exception as error:
            print(f"ERROR = {error}")
            if isinstance(error, HTTPException):
                raise error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_message(user_language, "auth.onboarding.onboarding_failed")
            )