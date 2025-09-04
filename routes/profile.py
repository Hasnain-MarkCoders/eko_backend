from fastapi import APIRouter, Depends, Request
from controllers.profile_controller import ProfileController
from schemas.profile import ChangeNameRequest, ChangeImageRequest, UpdateTokenRequest
from schemas.response import StandardResponse
from middleware.auth import get_current_user

router = APIRouter(prefix="/profile", tags=["Profile Management"])
profile_controller = ProfileController()

@router.put("/change-name", response_model=StandardResponse)
async def change_name(request: ChangeNameRequest, current_user: dict = Depends(get_current_user), http_request: Request = None):
    """Change user's display name"""
    user_language = getattr(http_request.state, 'user_language', 'en')
    return await profile_controller.change_name(current_user["_id"], request.newName, user_language)

@router.put("/change-image", response_model=StandardResponse)
async def change_image(request: ChangeImageRequest, current_user: dict = Depends(get_current_user), http_request: Request = None):
    """Change user's profile image"""
    user_language = getattr(http_request.state, 'user_language', 'en')
    return await profile_controller.change_image(current_user["_id"], request.image_url, user_language)

@router.delete("/delete", response_model=StandardResponse)
async def delete_user(current_user: dict = Depends(get_current_user), http_request: Request = None):
    """Delete user account"""
    user_language = getattr(http_request.state, 'user_language', 'en')
    return await profile_controller.delete_user(current_user["_id"], user_language)

@router.get("/is-active", response_model=StandardResponse)
async def is_active(current_user: dict = Depends(get_current_user), http_request: Request = None):
    """Check if user account is active"""
    user_language = getattr(http_request.state, 'user_language', 'en')
    return await profile_controller.is_active(current_user["_id"], user_language)

@router.get("/user", response_model=StandardResponse)
async def get_user(current_user: dict = Depends(get_current_user), http_request: Request = None):
    """Get current user's profile"""
    user_language = getattr(http_request.state, 'user_language', 'en')
    return await profile_controller.get_user(current_user["_id"], user_language)

@router.get("/welcome1", response_model=StandardResponse)
async def welcome1(current_user: dict = Depends(get_current_user), http_request: Request = None):
    """Check user's welcome status"""
    user_language = getattr(http_request.state, 'user_language', 'en')
    return await profile_controller.welcome1(current_user["_id"], user_language)

@router.put("/welcome2", response_model=StandardResponse)
async def welcome2(current_user: dict = Depends(get_current_user), http_request: Request = None):
    """Update user's welcome status"""
    user_language = getattr(http_request.state, 'user_language', 'en')
    return await profile_controller.welcome2(current_user["_id"], user_language)

@router.put("/update-token", response_model=StandardResponse)
async def update_token(request: UpdateTokenRequest, current_user: dict = Depends(get_current_user), http_request: Request = None):
    """Update user's notification token"""
    user_language = getattr(http_request.state, 'user_language', 'en')
    return await profile_controller.update_token(current_user["_id"], request.notificationToken, user_language) 

@router.get("/debug-name/{user_id}", response_model=StandardResponse)
async def debug_user_name(user_id: str, http_request: Request = None):
    language = http_request.headers.get("Accept-Language", "en")[:2] if http_request else "en"
    if language not in ["en", "fr"]:
        language = "en"
    return await profile_controller.debug_user_name(user_id, language)