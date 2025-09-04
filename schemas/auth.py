from pydantic import BaseModel, EmailStr, Field, validator
from typing import Literal
from .enums import Language, LanguageRequest

class EmailPasswordSignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    confirm_password: str = Field(..., description="Password confirmation")
    language: LanguageRequest = Field(default=LanguageRequest.EN, description="User's preferred language (EN or FR)")
    agreed: bool = Field(..., description="User must agree to privacy policy")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('agreed')
    def must_agree(cls, v):
        if not v:
            raise ValueError('You must agree to the privacy policy to continue')
        return v

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
    language: LanguageRequest = Field(..., description="User's preferred language (EN or FR)")
    purpose: Literal["personal assistance", "business", "education", "entertainment", "health", "productivity", "social", "other"] = Field(..., description="User's purpose for using the app")

class OnboardingResponse(BaseModel):
    success: bool
    message: str
    data: dict
