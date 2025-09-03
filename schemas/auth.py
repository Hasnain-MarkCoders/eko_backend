from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class EmailPasswordSignupRequest(BaseModel):
    email: EmailStr
    password: str

class EmailPasswordLoginRequest(BaseModel):
    email: EmailStr
    password: str

class EmailPasswordResponse(BaseModel):
    user: dict
    message: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class OnboardingRequest(BaseModel):
    name: str = Field(..., min_length=1, description="User's display name")
    age: int = Field(..., gt=0, le=120, description="User's age")
    gender: Literal["male", "female", "other"] = Field(..., description="User's gender")
    language: Literal["english", "spanish", "french", "german", "italian", "portuguese", "chinese", "japanese", "korean", "arabic", "hindi"] = Field(..., description="User's preferred language")
    purpose: Literal["personal assistance", "business", "education", "entertainment", "health", "productivity", "social", "other"] = Field(..., description="User's purpose for using the app")

class OnboardingResponse(BaseModel):
    success: bool
    message: str
    data: dict
