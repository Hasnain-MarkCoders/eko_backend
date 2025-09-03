from fastapi import APIRouter, Depends, HTTPException, status
from controllers.auth_controller import AuthController
from schemas.auth import (
    EmailPasswordSignupRequest,
    EmailPasswordLoginRequest,
    EmailPasswordResponse,
    ForgotPasswordRequest,
    OnboardingRequest,
    OnboardingResponse
)
from middleware.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_controller = AuthController()

@router.post("/signup")
async def email_password_signup(request: EmailPasswordSignupRequest):
    """Email/password signup endpoint"""
    return await auth_controller.email_password_signup(request.email, request.password)

@router.post("/login")
async def email_password_login(request: EmailPasswordLoginRequest):
    """Email/password login endpoint"""
    return await auth_controller.email_password_login(request.email, request.password)

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Forgot password endpoint"""
    return await auth_controller.forgot_password(request.email)

@router.post("/onboarding", response_model=OnboardingResponse)
async def onboarding(request: OnboardingRequest, current_user: dict = Depends(get_current_user)):
    """Complete user onboarding with additional profile information"""
    return await auth_controller.onboarding(
        current_user["_id"],
        request.name,
        request.age,
        request.gender,
        request.language,
        request.purpose
    )
