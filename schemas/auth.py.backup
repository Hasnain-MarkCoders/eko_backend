from pydantic import BaseModel, EmailStr

class FirebaseAuthRequest(BaseModel):
    accessToken: str
    name: str
    provider: str

class FirebaseAuthResponse(BaseModel):
    user: dict

class EmailPasswordSignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class EmailPasswordLoginRequest(BaseModel):
    email: EmailStr
    password: str

class EmailPasswordResponse(BaseModel):
    user: dict
    message: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr 