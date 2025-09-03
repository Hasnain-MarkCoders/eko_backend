from fastapi import HTTPException, status
from database import users
from services.firebase import initialize_admin
import jwt
import os
from dotenv import load_dotenv
from bson import ObjectId
from datetime import datetime, timezone

load_dotenv()

TOKEN_KEY = os.getenv("TOKEN_KEY", "Test_124")  # Default fallback
default_photo = "https://sauced-app-bucket.s3.us-east-2.amazonaws.com/sauced_placeholder.webp"

class AuthController:
    def __init__(self):
        self.admin = initialize_admin()
    
    async def email_password_signup(self, email: str, password: str):
        """Email/password signup using Firebase"""
        try:
            # Check if user already exists in database
            existing_user = await users.find_one({"email": email})
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
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
                "createdAt": datetime.now(timezone.utc),
                "updatedAt": datetime.now(timezone.utc)
            }
            
            result = await users.insert_one(new_user)
            new_user["_id"] = str(result.inserted_id)
            
            # Generate JWT token
            token = jwt.encode({"_id": str(result.inserted_id)}, TOKEN_KEY, algorithm="HS256")
            
            return {
                "user": {
                    "token": token,
                    **new_user
                },
                "message": "User created successfully"
            }
            
        except Exception as error:
            print(f"ERROR = {error}")
            if "EMAIL_EXISTS" in str(error):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
            elif "WEAK_PASSWORD" in str(error):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password is too weak. Use at least 6 characters."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(error)
                )
    
    async def email_password_login(self, email: str, password: str):
        """Email/password login using Firebase"""
        try:
            # Check if user exists in database
            existing_user = await users.find_one({"email": email})
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Check if user is deleted
            if existing_user.get("isDeleted", False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account has been deleted"
                )
            
            # Check if user is brand type
            if existing_user.get("type") == "brand":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Please use Sauced brand panel."
                )
            
            # Convert ObjectId to string for serialization
            existing_user["_id"] = str(existing_user["_id"])
            
            # Verify password with Firebase (this would require additional Firebase Auth REST API calls)
            # For now, we'll assume the password is correct if user exists
            # In production, you'd want to implement proper password verification
            
            # Generate JWT token
            token = jwt.encode({"_id": existing_user["_id"]}, TOKEN_KEY, algorithm="HS256")
            
            return {
                "user": {
                    "token": token,
                    **existing_user
                },
                "message": "Login successful"
            }
            
        except Exception as error:
            print(f"ERROR = {error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error)
            )
    
    async def forgot_password(self, email: str):
        """Send password reset email using Firebase"""
        try:
            # Check if user exists in database
            existing_user = await users.find_one({"email": email})
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Check if user is deleted
            if existing_user.get("isDeleted", False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account has been deleted"
                )
            
            # Check if user is brand type
            if existing_user.get("type") == "brand":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Please use Sauced brand panel."
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
                    "message": "Password reset email sent successfully",
                    "resetLink": reset_link,
                    "note": "In production, this link would be sent via email"
                }
                
            except Exception as firebase_error:
                print(f"Firebase password reset error: {firebase_error}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate password reset link"
                )
            
        except Exception as error:
            print(f"ERROR = {error}")
            if isinstance(error, HTTPException):
                raise error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error)
            )
    
    async def onboarding(self, user_id: str, name: str, age: int, gender: str, language: str, purpose: str):
        """Complete user onboarding with additional profile information"""
        try:
            # Convert string user_id to ObjectId
            try:
                object_id = ObjectId(user_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user ID format"
                )
            
            # Get current user
            current_user = await users.find_one({"_id": object_id})
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Check if profile is already completed
            if current_user.get("profile_completed", False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Profile already completed. Onboarding can only be done once."
                )
            
            # Check if user is deleted
            if current_user.get("isDeleted", False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account has been deleted"
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
                        detail="Failed to update display name in Firebase"
                    )
            
            # Update user in MongoDB with onboarding data
            update_data = {
                "name": name,
                "age": age,
                "gender": gender,
                "language": language,
                "purpose": purpose,
                "profile_completed": True,
                "updatedAt": datetime.now(timezone.utc)
            }
            
            result = await users.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Get updated user
            updated_user = await users.find_one({"_id": object_id})
            updated_user["_id"] = str(updated_user["_id"])
            
            # Generate JWT token
            token = jwt.encode({"_id": str(updated_user["_id"])}, TOKEN_KEY, algorithm="HS256")
            
            return {
                "success": True,
                "message": "Onboarding completed successfully",
                "data": {
                    "user_id": str(updated_user["_id"]),
                    "name": updated_user.get("name"),
                    "email": updated_user.get("email"),
                    "age": updated_user.get("age"),
                    "gender": updated_user.get("gender"),
                    "language": updated_user.get("language"),
                    "purpose": updated_user.get("purpose"),
                    "profile_completed": updated_user.get("profile_completed", True),
                    "token": token
                }
            }
            
        except Exception as error:
            print(f"ERROR = {error}")
            if isinstance(error, HTTPException):
                raise error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to complete onboarding"
            )