from fastapi import APIRouter, Depends
from controllers.profile_controller import ProfileController
from schemas.profile import ChangeNameRequest, ChangeImageRequest, UpdateTokenRequest
from middleware.auth import get_current_user

router = APIRouter(prefix="/profile", tags=["Profile Management"])
profile_controller = ProfileController()

@router.put("/change-name")
async def change_name(request: ChangeNameRequest, current_user: dict = Depends(get_current_user)):
    """Change user's display name"""
    return await profile_controller.change_name(current_user["_id"], request.newName)

@router.put("/change-image")
async def change_image(request: ChangeImageRequest, current_user: dict = Depends(get_current_user)):
    """Change user's profile image"""
    return await profile_controller.change_image(current_user["_id"], request.image_url)

@router.delete("/delete")
async def delete_user(current_user: dict = Depends(get_current_user)):
    """Delete user account"""
    return await profile_controller.delete_user(current_user["_id"])

@router.get("/is-active")
async def is_active(current_user: dict = Depends(get_current_user)):
    """Check if user account is active"""
    return await profile_controller.is_active(current_user["_id"])

@router.get("/user")
async def get_user(current_user: dict = Depends(get_current_user)):
    """Get current user's profile"""
    return await profile_controller.get_user(current_user["_id"])

@router.get("/welcome1")
async def welcome1(current_user: dict = Depends(get_current_user)):
    """Check user's welcome status"""
    return await profile_controller.welcome1(current_user["_id"])

@router.put("/welcome2")
async def welcome2(current_user: dict = Depends(get_current_user)):
    """Update user's welcome status"""
    return await profile_controller.welcome2(current_user["_id"])

@router.put("/update-token")
async def update_token(request: UpdateTokenRequest, current_user: dict = Depends(get_current_user)):
    """Update user's notification token"""
    return await profile_controller.update_token(current_user["_id"], request.notificationToken) 