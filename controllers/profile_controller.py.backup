from fastapi import HTTPException, status
from database import users
from services.firebase import initialize_admin
from datetime import datetime, timezone
from bson import ObjectId

class ProfileController:
    def __init__(self):
        self.admin = initialize_admin()
    
    async def change_name(self, user_id: str, new_name: str):
        """Change user's display name"""
        if not new_name or new_name.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name cannot be empty"
            )
        
        try:
            # Convert string user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # Check if new name is same as current name
        current_user = await users.find_one({"_id": object_id})
        if current_user and current_user.get("name") == new_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New name cannot be the same as current name"
            )
        
        # Update name in database
        result = await users.update_one(
            {"_id": object_id},
            {"$set": {"name": new_name, "updatedAt": datetime.now(timezone.utc)}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get updated user
        updated_user = await users.find_one({"_id": object_id})
        updated_user["_id"] = str(updated_user["_id"])
        
        return {
            "message": "User Name Changed Successfully",
            "user": updated_user
        }
    
    async def change_image(self, user_id: str, image_url: str):
        """Change user's profile image"""
        if not image_url or image_url.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image URL cannot be empty"
            )
        
        try:
            # Convert string user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # Update image in database
        result = await users.update_one(
            {"_id": object_id},
            {"$set": {"image": image_url, "updatedAt": datetime.now(timezone.utc)}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get updated user
        updated_user = await users.find_one({"_id": object_id})
        updated_user["_id"] = str(updated_user["_id"])
        
        return {
            "message": "User Image Changed Successfully",
            "user": updated_user
        }
    
    async def delete_user(self, user_id: str):
        """Delete user account from both database and Firebase"""
        try:
            try:
                # Convert string user_id to ObjectId
                object_id = ObjectId(user_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user ID format"
                )
            
            # Get user details first
            user = await users.find_one({"_id": object_id})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Delete user from Firebase
            if user.get("uid"):
                try:
                    self.admin.auth.delete_user(user["uid"])
                except Exception as e:
                    print(f"Firebase deletion error: {e}")
                    # Continue with database deletion even if Firebase fails
            
            # Delete user from database
            result = await users.delete_one({"_id": object_id})
            
            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return {
                "message": "User Deleted Successfully"
            }
            
        except Exception as e:
            print(f"ERROR = {e}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )
    
    async def is_active(self, user_id: str):
        """Check if user account is active"""
        try:
            # Convert string user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        user = await users.find_one({"_id": object_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"status": user.get("status", "inactive")}
    
    async def get_user(self, user_id: str):
        """Get current user's profile"""
        try:
            # Convert string user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        user = await users.find_one({"_id": object_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user["_id"] = str(user["_id"])
        return {"user": user}
    
    async def welcome1(self, user_id: str):
        """Check user's welcome status"""
        return {"message": "Welcome 1"}
    
    async def welcome2(self, user_id: str):
        """Update user's welcome status"""
        try:
            # Convert string user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        result = await users.update_one(
            {"_id": object_id},
            {"$set": {"welcome": False, "updatedAt": datetime.now(timezone.utc)}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get updated user
        updated_user = await users.find_one({"_id": object_id})
        updated_user["_id"] = str(updated_user["_id"])
        
        return {
            "message": "Welcome 2",
            "user": updated_user
        }
    
    async def update_token(self, user_id: str, notification_token: str):
        """Update user's notification token"""
        try:
            # Convert string user_id to ObjectId
            object_id = ObjectId(user_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        result = await users.update_one(
            {"_id": object_id},
            {"$set": {"notificationToken": notification_token, "updatedAt": datetime.now(timezone.utc)}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get updated user
        updated_user = await users.find_one({"_id": object_id})
        updated_user["_id"] = str(updated_user["_id"])
        
        return {
            "message": "Notification Token Updated Successfully",
            "user": updated_user
        } 