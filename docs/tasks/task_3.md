# Task 3: Enhance Signup API with Password Validation and Language Support

## Overview
Revamp the signup API to include comprehensive password validation, confirmation password field, and language selection. This will improve security and user experience by ensuring strong passwords and supporting multiple languages from the start.

## Current Signup API Issues

### 1. Missing Password Confirmation
- No `confirm_password` field in request body
- No validation to ensure passwords match
- Users can make typos in password without knowing

### 2. Weak Password Validation
- Only basic Firebase validation (minimum 6 characters)
- No comprehensive password strength checks
- No validation for common weak passwords

### 3. Missing Language Support
- No language selection during signup
- Language is only collected during onboarding
- Users can't set their preferred language upfront

## Implementation Requirements

### 1. Enhanced Request Schema

#### Current Request Body
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

#### New Request Body
```json
{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!",
    "language": "english"
}
```

### 2. Password Validation Rules

Implement comprehensive password validation:

#### Minimum Requirements
- **Length**: Minimum 8 characters (increased from 6)
- **Uppercase**: At least 1 uppercase letter
- **Lowercase**: At least 1 lowercase letter
- **Numbers**: At least 1 number
- **Special Characters**: At least 1 special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

#### Additional Security Checks
- **Common Passwords**: Reject common weak passwords (password, 123456, qwerty, etc.)
- **Email Similarity**: Password should not be too similar to email
- **Sequential Characters**: Reject passwords with sequential characters (abc123, 123456)
- **Repeated Characters**: Reject passwords with too many repeated characters (aaa111)

### 3. Language Support

#### Supported Languages
- `"english"` - English (default)
- `"french"` - French

#### Language Validation
- Must be one of the supported languages
- Default to "english" if not provided
- Store language in user profile during signup

### 4. Enhanced Response Format

#### Success Response
```json
{
    "success": true,
    "message": "User created successfully",
    "data": {
        "user_id": "68b8a995e7ba49575d5fed4c",
        "uid": "mBENSps9jDeqEJN7WBlfeCXC2pE2",
        "email": "user@example.com",
        "name": "",
        "provider": "password",
        "status": "active",
        "welcome": true,
        "image": "https://sauced-app-bucket.s3.us-east-2.amazonaws.com/sauced_placeholder.webp",
        "type": "user",
        "notificationToken": "",
        "isDeleted": false,
        "language": "english",
        "createdAt": "2025-09-03T20:48:21.854000",
        "updatedAt": "2025-09-03T20:48:21.854000",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

## Implementation Steps

### 1. Update Request Schema

Create new schema in `schemas/auth.py`:

```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Literal
import re

class EnhancedSignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    confirm_password: str = Field(..., description="Password confirmation")
    language: Literal["english", "french"] = Field(default="english", description="User's preferred language")
    
    @validator('password')
    def validate_password(cls, v):
        # Check minimum length
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for uppercase letter
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        # Check for lowercase letter
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        # Check for number
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        # Check for special character
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', v):
            raise ValueError('Password must contain at least one special character')
        
        # Check for common weak passwords
        common_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey',
            '1234567890', 'password1', 'qwerty123', 'dragon', 'master'
        ]
        if v.lower() in common_passwords:
            raise ValueError('Password is too common. Please choose a stronger password')
        
        # Check for sequential characters
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', v.lower()):
            raise ValueError('Password cannot contain sequential characters')
        
        # Check for repeated characters
        if re.search(r'(.)\1{2,}', v):
            raise ValueError('Password cannot contain more than 2 repeated characters in a row')
        
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
```

### 2. Update User Model

Add language field to user model in `models/user.py`:

```python
class UserModel(BaseModel):
    # ... existing fields ...
    language: Optional[str] = "english"  # Add language field with default
    # ... rest of fields ...
```

### 3. Update Auth Controller

Modify `email_password_signup` method in `controllers/auth_controller.py`:

```python
async def email_password_signup(self, email: str, password: str, confirm_password: str, language: str = "english"):
    """Enhanced email/password signup with validation"""
    try:
        # Validate password confirmation
        if password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        
        # Check if user already exists in database
        existing_user = await users.find_one({"email": email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user in Firebase
        user_properties = {
            "email": email,
            "password": password,
            "email_verified": False
        }
        
        firebase_user = self.admin.auth.create_user(**user_properties)
        uid = firebase_user.uid
        
        # Create user in database with language
        new_user = {
            "uid": uid,
            "email": email,
            "name": "",  # Empty name initially, will be set during onboarding
            "provider": "password",
            "status": "active",
            "welcome": True,
            "image": default_photo,
            "type": "user",
            "notificationToken": "",
            "isDeleted": False,
            "language": language,  # Store selected language
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc)
        }
        
        result = await users.insert_one(new_user)
        new_user["_id"] = str(result.inserted_id)
        
        # Generate JWT token
        token = jwt.encode({"_id": str(result.inserted_id)}, TOKEN_KEY, algorithm="HS256")
        
        return {
            "success": True,
            "message": "User created successfully",
            "data": {
                "user_id": str(result.inserted_id),
                "uid": uid,
                "email": email,
                "name": "",
                "provider": "password",
                "status": "active",
                "welcome": True,
                "image": default_photo,
                "type": "user",
                "notificationToken": "",
                "isDeleted": False,
                "language": language,
                "createdAt": new_user["createdAt"].isoformat(),
                "updatedAt": new_user["updatedAt"].isoformat(),
                "token": token
            }
        }
        
    except Exception as error:
        # ... existing error handling ...
```

### 4. Update Route

Modify the signup route in `routes/auth.py`:

```python
@router.post("/signup", response_model=StandardResponse)
async def email_password_signup(request: EnhancedSignupRequest):
    """Enhanced email/password signup endpoint with validation"""
    return await auth_controller.email_password_signup(
        request.email, 
        request.password, 
        request.confirm_password, 
        request.language
    )
```

### 5. Update Documentation

**CRITICAL**: Update API documentation to reflect the new signup endpoint:

#### Documentation Update Requirements:
- Update `docs/documentation.md` with new request body format
- Add `confirm_password` field documentation
- Add `language` field documentation with supported values
- Update response format to use standardized structure
- Document all new password validation rules
- Add error response examples for each validation failure
- Update Postman collection with new request format
- Ensure documentation matches the actual implementation

## Error Handling

### Password Validation Errors
- `400 Bad Request` - Password too short
- `400 Bad Request` - Missing uppercase letter
- `400 Bad Request` - Missing lowercase letter
- `400 Bad Request` - Missing number
- `400 Bad Request` - Missing special character
- `400 Bad Request` - Password too common
- `400 Bad Request` - Sequential characters detected
- `400 Bad Request` - Too many repeated characters
- `400 Bad Request` - Passwords do not match

### Language Validation Errors
- `400 Bad Request` - Unsupported language (if not english/french)

## Testing

Create comprehensive test cases for:

### Password Validation Tests
- Valid strong passwords
- Weak passwords (too short, no uppercase, etc.)
- Common passwords
- Sequential characters
- Repeated characters
- Password confirmation mismatch

### Language Tests
- English language selection
- French language selection
- Default language (english)
- Invalid language values

### Integration Tests
- Complete signup flow with valid data
- Error handling for various validation failures
- Database storage verification
- Firebase user creation verification

## Benefits

1. **Enhanced Security**: Strong password requirements prevent weak passwords
2. **Better UX**: Password confirmation prevents typos
3. **Language Support**: Users can set their preferred language from signup
4. **Consistency**: Language is available throughout the user journey
5. **Validation**: Comprehensive input validation prevents common issues

## Migration Notes

- This is a breaking change for existing frontend applications
- Frontend must be updated to include `confirm_password` and `language` fields
- Existing users will have `language: "english"` as default
- **MANDATORY**: Update API documentation and Postman collections to reflect new request/response format
- **CRITICAL**: Update `docs/documentation.md` with new signup endpoint specification
- **REQUIRED**: Add new password validation rules to documentation
- **ESSENTIAL**: Document new language field and supported values

## Future Considerations

- Consider adding password strength meter in frontend
- Implement password history to prevent reuse
- Add rate limiting for signup attempts
- Consider implementing email verification before account activation
