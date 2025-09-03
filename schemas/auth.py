from pydantic import BaseModel, EmailStr

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
