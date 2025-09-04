from fastapi import HTTPException, status
from database import users
from services.firebase import initialize_admin
from datetime import datetime, timezone
from bson import ObjectId
import uuid
from locales import get_message

class ProfileController:
    def __init__(self):
        self.admin = initialize_admin()
    
    async def change_name(self, user_id: str, new_name: str, language: str = "en"):
        """Change user's display name in both MongoDB and Firebase"""
        if not new_name or new_name.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_message(language, "profile.change_name.name_empty")
            )
        
        try:
            # Convert string user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_message(language, "general.invalid_user_id")
            )
        
        # Get current user to check existing name and get Firebase UID
        current_user = await users.find_one({"_id": object_id})
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_message(language, "profile.change_name.user_not_found")
            )
        
        # Check if new name is same as current name
        if current_user.get("name") == new_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_message(language, "profile.change_name.same_name")
            )
        
        # Update name in Firebase first
        firebase_uid = current_user.get("uid")
        if firebase_uid:
            try:
                self.admin.auth.update_user(
                    firebase_uid,
                    display_name=new_name
                )
                print(f"✅ Firebase display name updated for user {firebase_uid}")
            except Exception as e:
                print(f"❌ Firebase update error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=get_message(language, "profile.change_name.firebase_update_failed")
                )
        
        # Update name in MongoDB
        result = await users.update_one(
            {"_id": object_id},
            {"$set": {"name": new_name, "updatedAt": datetime.now(timezone.utc)}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_message(language, "general.user_not_found")
            )
        
        # Get updated user
        updated_user = await users.find_one({"_id": object_id})
        updated_user["_id"] = str(updated_user["_id"])
        
        return {
            "success": True,
            "message": get_message(language, "profile.change_name.success"),
            "data": {
                "user_id": updated_user["_id"],
                "name": updated_user["name"],
                "email": updated_user["email"],
                "updatedAt": updated_user["updatedAt"]
            }
        }
    
    async def change_image(self, user_id: str, image_url: str, language: str = "en"):
        """Change user's profile image"""
        if not image_url or image_url.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_message(language, "profile.change_image.image_empty")
            )
        
        try:
            # Convert string user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_message(language, "general.invalid_user_id")
            )
        
        # Update image in database
        result = await users.update_one(
            {"_id": object_id},
            {"$set": {"image": image_url, "updatedAt": datetime.now(timezone.utc)}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_message(language, "general.user_not_found")
            )
        
        # Get updated user
        updated_user = await users.find_one({"_id": object_id})
        updated_user["_id"] = str(updated_user["_id"])
        
        return {
            "success": True,
            "message": get_message(language, "profile.change_image.success"),
            "data": {
                "user_id": updated_user["_id"],
                "name": updated_user["name"],
                "email": updated_user["email"],
                "image": updated_user["image"],
                "updatedAt": updated_user["updatedAt"]
            }
        }
    
    async def delete_user(self, user_id: str, language: str = "en"):
        """Soft delete user account (Reddit-style deletion)"""
        try:
            try:
                # Convert string user_id to ObjectId
                object_id = ObjectId(user_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(language, "general.invalid_user_id")
                )
            
            # Get user details first
            user = await users.find_one({"_id": object_id})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(language, "general.user_not_found")
                )
            
            # Check if user is already deleted
            if user.get("isDeleted", False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(language, "profile.delete.already_deleted")
                )
            
            # Generate a unique deleted username to avoid conflicts
            deleted_username = f"deleted_user_{uuid.uuid4().hex[:8]}"
            deleted_email = f"deleted_{uuid.uuid4().hex[:8]}@deleted.local"
            
            # Soft delete: Update user record instead of removing it
            update_data = {
                "isDeleted": True,
                "status": "deleted",
                "name": deleted_username,
                "email": deleted_email,
                "image": "https://sauced-app-bucket.s3.us-east-2.amazonaws.com/sauced_placeholder.webp",
                "notificationToken": "",
                "updatedAt": datetime.now(timezone.utc),
                "deletedAt": datetime.now(timezone.utc)
            }
            
            # Update user in database (soft delete)
            result = await users.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(language, "general.user_not_found")
                )
            
            # Delete user from Firebase (hard delete from Firebase)
            if user.get("uid"):
                try:
                    self.admin.auth.delete_user(user["uid"])
                    print(f"✅ Firebase user {user['uid']} deleted successfully")
                except Exception as e:
                    print(f"❌ Firebase deletion error: {e}")
                    # Continue even if Firebase deletion fails
                    # The user is already soft-deleted in our database
            
            return {
                "success": True,
                "message": get_message(language, "profile.delete.success"),
                "data": {
                    "note": "Account has been deactivated and personal information removed. Firebase account has been deleted."
                }
            }
            
        except Exception as e:
            print(f"ERROR = {e}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_message(language, "general.internal_error")
            )
    
    async def is_active(self, user_id: str, language: str = "en"):
        """Check if user account is active"""
        try:
            # Convert string user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_message(language, "general.invalid_user_id")
            )
        
        user = await users.find_one({"_id": object_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_message(language, "general.user_not_found")
            )
        
        return {
            "success": True,
            "message": get_message(language, "profile.is_active.success"),
            "data": {
                "status": user.get("status", "inactive")
            }
        }
    
    async def get_user(self, user_id: str, language: str = "en"):
        """Get current user's profile"""
        try:
            # Convert string user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_message(language, "general.invalid_user_id")
            )
        
        user = await users.find_one({"_id": object_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_message(language, "general.user_not_found")
            )
        
        user["_id"] = str(user["_id"])
        return {
            "success": True,
            "message": get_message(language, "profile.get_user.success"),
            "data": {
                "user_id": user["_id"],
                "name": user["name"],
                "email": user["email"],
                "image": user["image"],
                "status": user["status"],
                "welcome": user["welcome"],
                "notificationToken": user["notificationToken"],
                "age": user.get("age"),
                "gender": user.get("gender"),
                "language": user.get("language"),
                "purpose": user.get("purpose"),
                "createdAt": user["createdAt"],
                "updatedAt": user["updatedAt"]
            }
        }
    
    async def welcome1(self, user_id: str, language: str = "en"):
        """Check user's welcome status"""
        return {
            "success": True,
            "message": get_message(language, "profile.welcome.welcome1"),
            "data": None
        }
    
    async def welcome2(self, user_id: str, language: str = "en"):
        """Update user's welcome status"""
        try:
            # Convert string user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_message(language, "general.invalid_user_id")
            )
        
        result = await users.update_one(
            {"_id": object_id},
            {"$set": {"welcome": False, "updatedAt": datetime.now(timezone.utc)}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_message(language, "general.user_not_found")
            )
        
        # Get updated user
        updated_user = await users.find_one({"_id": object_id})
        updated_user["_id"] = str(updated_user["_id"])
        
        return {
            "success": True,
            "message": get_message(language, "profile.welcome.welcome2"),
            "data": {
                "user_id": updated_user["_id"],
                "name": updated_user["name"],
                "email": updated_user["email"],
                "welcome": updated_user["welcome"],
                "updatedAt": updated_user["updatedAt"]
            }
        }
    
    async def update_token(self, user_id: str, notification_token: str, language: str = "en"):
        """Update user's notification token"""
        try:
            # Convert string user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_message(language, "general.invalid_user_id")
            )
        
        result = await users.update_one(
            {"_id": object_id},
            {"$set": {"notificationToken": notification_token, "updatedAt": datetime.now(timezone.utc)}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_message(language, "general.user_not_found")
            )
        
        # Get updated user
        updated_user = await users.find_one({"_id": object_id})
        updated_user["_id"] = str(updated_user["_id"])
        
        return {
            "success": True,
            "message": get_message(language, "profile.update_token.success"),
            "data": {
                "user_id": updated_user["_id"],
                "name": updated_user["name"],
                "email": updated_user["email"],
                "notificationToken": updated_user["notificationToken"],
                "updatedAt": updated_user["updatedAt"]
            }
        }

    async def debug_user_name(self, user_id: str, language: str = "en"):
        # Debug: Compare display name in MongoDB vs Firebase
        try:
            # Convert user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_message(language, "general.invalid_user_id")
            )

        # Get user from MongoDB
        mongo_user = await users.find_one({"_id": object_id})
        if not mongo_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=get_message(language, "profile.debug_name.user_not_found")
            )

        firebase_name = None
        firebase_uid = mongo_user.get("uid")

        # Fetch displayName from Firebase
        if firebase_uid:
            try:
                firebase_user = self.admin.auth.get_user(firebase_uid)
                firebase_name = firebase_user.display_name
            except Exception as e:
                firebase_name = f"❌ Failed to fetch from Firebase: {e}"

        return {
            "success": True,
            "message": get_message(language, "profile.debug_name.success"),
            "data": {
                "mongo": {
                    "uid": firebase_uid,
                    "name": mongo_user.get("name"),
                    "email": mongo_user.get("email")
                },
                "firebase": {
                    "uid": firebase_uid,
                    "display_name": firebase_name
                }
            }
        }
