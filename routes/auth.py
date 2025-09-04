from fastapi import APIRouter, Depends, HTTPException, status, Request
from controllers.auth_controller import AuthController
from schemas.auth import (
    EmailPasswordSignupRequest,
    EmailPasswordLoginRequest,
    EmailPasswordResponse,
    ForgotPasswordRequest,
    OnboardingRequest,
    OnboardingResponse
)
from schemas.response import StandardResponse
from middleware.auth import get_current_user, get_language_from_request

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_controller = AuthController()

@router.post("/signup", response_model=StandardResponse)
async def email_password_signup(request: EmailPasswordSignupRequest, http_request: Request):
    """Email/password signup endpoint"""
    language = get_language_from_request(http_request)
    return await auth_controller.email_password_signup(request.email, request.password, language)

@router.post("/login", response_model=StandardResponse)
async def email_password_login(request: EmailPasswordLoginRequest, http_request: Request):
    """Email/password login endpoint"""
    language = get_language_from_request(http_request)
    return await auth_controller.email_password_login(request.email, request.password, language)

@router.post("/forgot-password", response_model=StandardResponse)
async def forgot_password(request: ForgotPasswordRequest, http_request: Request):
    """Forgot password endpoint"""
    language = get_language_from_request(http_request)
    return await auth_controller.forgot_password(request.email, language)

@router.post("/onboarding", response_model=StandardResponse)
async def onboarding(request: OnboardingRequest, current_user: dict = Depends(get_current_user), http_request: Request = None):
    """Complete user onboarding with additional profile information"""
    # Use user's language preference from request state (set by auth middleware)
    user_language = getattr(http_request.state, 'user_language', 'en')
    return await auth_controller.onboarding(
        current_user["_id"],
        request.name,
        request.age,
        request.gender,
        request.language,
        request.purpose,
        user_language
    )
