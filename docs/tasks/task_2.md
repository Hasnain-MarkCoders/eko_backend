# Task 2: Standardize API Response Formats

## Overview
Standardize all API response formats to use a consistent structure across the entire application. Currently, different endpoints use different response formats which creates inconsistency and confusion for frontend developers.

## Problem Statement

### Current Inconsistent Response Formats

#### 1. Signup/Login APIs (Inconsistent Format)
```json
{
    "user": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "_id": "68b8a995e7ba49575d5fed4c",
        "uid": "mBENSps9jDeqEJN7WBlfeCXC2pE2",
        "email": "shahzaib.ali.khawaja@gmail.com",
        "name": "Shahzaib",
        "provider": "password",
        "status": "active",
        "welcome": true,
        "image": "https://sauced-app-bucket.s3.us-east-2.amazonaws.com/sauced_placeholder.webp",
        "type": "user",
        "notificationToken": "",
        "isDeleted": false,
        "createdAt": "2025-09-03T20:48:21.854000",
        "updatedAt": "2025-09-03T21:42:15.985000"
    },
    "message": "Login successful"
}
```

#### 2. Onboarding API (Correct Format)
```json
{
    "success": true,
    "message": "Onboarding completed successfully",
    "data": {
        "user_id": "68b8cc77988d9815dd6588e3",
        "name": "John Doe",
        "email": "shahzaib.ali.khawaja1@gmail.com",
        "age": 25,
        "gender": "male",
        "language": "english",
        "purpose": "personal assistance",
        "welcome": false,
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

## Standard Response Format

### Target Format Structure
All API responses should follow this consistent structure:

```json
{
    "success": boolean,
    "message": string,
    "data": object | array | null
}
```

### Field Specifications

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `success` | boolean | Yes | Indicates if the request was successful |
| `message` | string | Yes | Human-readable message describing the result |
| `data` | object/array/null | Yes | The actual response data (varies by endpoint) |

## Implementation Requirements

### 1. Update Authentication Endpoints

#### Signup API (`POST /auth/signup`)
**Current Response:**
```json
{
    "user": { ... },
    "message": "User created successfully"
}
```

**Target Response:**
```json
{
    "success": true,
    "message": "User created successfully",
    "data": {
        "user_id": "68b8a995e7ba49575d5fed4c",
        "uid": "mBENSps9jDeqEJN7WBlfeCXC2pE2",
        "email": "shahzaib.ali.khawaja@gmail.com",
        "name": "",
        "provider": "password",
        "status": "active",
        "welcome": true,
        "image": "https://sauced-app-bucket.s3.us-east-2.amazonaws.com/sauced_placeholder.webp",
        "type": "user",
        "notificationToken": "",
        "isDeleted": false,
        "createdAt": "2025-09-03T20:48:21.854000",
        "updatedAt": "2025-09-03T20:48:21.854000",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

#### Login API (`POST /auth/login`)
**Current Response:**
```json
{
    "user": { ... },
    "message": "Login successful"
}
```

**Target Response:**
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "user_id": "68b8a995e7ba49575d5fed4c",
        "uid": "mBENSps9jDeqEJN7WBlfeCXC2pE2",
        "email": "shahzaib.ali.khawaja@gmail.com",
        "name": "Shahzaib",
        "provider": "password",
        "status": "active",
        "welcome": true,
        "image": "https://sauced-app-bucket.s3.us-east-2.amazonaws.com/sauced_placeholder.webp",
        "type": "user",
        "notificationToken": "",
        "isDeleted": false,
        "createdAt": "2025-09-03T20:48:21.854000",
        "updatedAt": "2025-09-03T21:42:15.985000",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

#### Forgot Password API (`POST /auth/forgot-password`)
**Current Response:**
```json
{
    "message": "Password reset email sent successfully",
    "resetLink": "...",
    "note": "In production, this link would be sent via email"
}
```

**Target Response:**
```json
{
    "success": true,
    "message": "Password reset email sent successfully",
    "data": {
        "resetLink": "...",
        "note": "In production, this link would be sent via email"
    }
}
```

### 2. Update Profile Management Endpoints

#### Change Name API (`PUT /profile/change-name`)
**Current Response:**
```json
{
    "message": "User Name Changed Successfully",
    "user": { ... }
}
```

**Target Response:**
```json
{
    "success": true,
    "message": "User Name Changed Successfully",
    "data": {
        "user_id": "...",
        "name": "New Name",
        "email": "...",
        "updatedAt": "...",
        // ... other user fields
    }
}
```

#### Change Image API (`PUT /profile/change-image`)
**Current Response:**
```json
{
    "message": "User Image Changed Successfully",
    "user": { ... }
}
```

**Target Response:**
```json
{
    "success": true,
    "message": "User Image Changed Successfully",
    "data": {
        "user_id": "...",
        "name": "...",
        "email": "...",
        "image": "new_image_url",
        "updatedAt": "...",
        // ... other user fields
    }
}
```

#### Delete User API (`DELETE /profile/delete`)
**Current Response:**
```json
{
    "message": "User account deleted successfully",
    "note": "Account has been deactivated and personal information removed. Firebase account has been deleted."
}
```

**Target Response:**
```json
{
    "success": true,
    "message": "User account deleted successfully",
    "data": {
        "note": "Account has been deactivated and personal information removed. Firebase account has been deleted."
    }
}
```

#### Get User API (`GET /profile/user`)
**Current Response:**
```json
{
    "user": { ... }
}
```

**Target Response:**
```json
{
    "success": true,
    "message": "User profile retrieved successfully",
    "data": {
        "user_id": "...",
        "name": "...",
        "email": "...",
        // ... all user fields
    }
}
```

#### Is Active API (`GET /profile/is-active`)
**Current Response:**
```json
{
    "status": "active"
}
```

**Target Response:**
```json
{
    "success": true,
    "message": "User status retrieved successfully",
    "data": {
        "status": "active"
    }
}
```

#### Welcome APIs (`GET /profile/welcome1`, `PUT /profile/welcome2`)
**Current Response:**
```json
{
    "message": "Welcome 1"
}
```

**Target Response:**
```json
{
    "success": true,
    "message": "Welcome 1",
    "data": null
}
```

#### Update Token API (`PUT /profile/update-token`)
**Current Response:**
```json
{
    "message": "Notification Token Updated Successfully",
    "user": { ... }
}
```

**Target Response:**
```json
{
    "success": true,
    "message": "Notification Token Updated Successfully",
    "data": {
        "user_id": "...",
        "name": "...",
        "email": "...",
        "notificationToken": "new_token",
        "updatedAt": "...",
        // ... other user fields
    }
}
```

#### Debug Name API (`GET /profile/debug-name/{user_id}`)
**Current Response:**
```json
{
    "mongo": { ... },
    "firebase": { ... }
}
```

**Target Response:**
```json
{
    "success": true,
    "message": "Name comparison retrieved successfully",
    "data": {
        "mongo": { ... },
        "firebase": { ... }
    }
}
```

### 3. Update Utility Endpoints

#### Root API (`GET /`)
**Current Response:**
```json
{
    "message": "Welcome to Eko Backend API"
}
```

**Target Response:**
```json
{
    "success": true,
    "message": "Welcome to Eko Backend API",
    "data": null
}
```

#### Health Check API (`GET /health`)
**Current Response:**
```json
{
    "status": "healthy"
}
```

**Target Response:**
```json
{
    "success": true,
    "message": "API is healthy",
    "data": {
        "status": "healthy"
    }
}
```

## Implementation Steps

### 1. Create Standard Response Schemas
Create a new file `schemas/response.py` with standard response schemas:

```python
from pydantic import BaseModel
from typing import Any, Optional

class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    data: Optional[Any] = None
```

### 2. Update Controllers
Modify all controller methods to return the standardized format:
- Replace `{"user": ...}` with `{"success": True, "message": "...", "data": ...}`
- Replace `{"message": "..."}` with `{"success": True, "message": "...", "data": null}`
- Ensure all responses include the `success` field

### 3. Update Response Models
Update all response models in route files to use `StandardResponse`:
- Import `StandardResponse` from `schemas.response`
- Update route decorators to use `response_model=StandardResponse`

### 4. Update API Documentation
**CRITICAL**: Update the API documentation in `docs/documentation.md` to reflect the new standardized format. This is mandatory to maintain consistency between code and documentation.

#### Documentation Update Requirements:
- Update all endpoint response examples to use the new format
- Remove old response examples that use `"user"` key
- Add `"success"` and `"data"` fields to all response examples
- Update response field descriptions
- Ensure all endpoints are documented with correct response formats
- Verify no endpoints are missing from documentation
- Verify no documented endpoints are missing from code

## Benefits

1. **Consistency**: All endpoints follow the same response structure
2. **Predictability**: Frontend developers know what to expect from every endpoint
3. **Scalability**: Future endpoints (chat, notifications, etc.) will follow the same pattern
4. **Error Handling**: Consistent error response format across all endpoints
5. **Maintainability**: Easier to maintain and debug API responses

## Testing

Create test cases to verify:
- All endpoints return the standardized format
- Success responses include `success: true`
- Error responses include `success: false`
- Data is properly nested under the `data` key
- Messages are consistent and descriptive

## Migration Notes

- This is a breaking change for frontend applications
- Frontend code will need to be updated to access data via `response.data` instead of `response.user`
- Consider versioning the API if backward compatibility is required
- **MANDATORY**: Update all API documentation and Postman collections to reflect new response format
- **CRITICAL**: Ensure documentation is updated before deployment to prevent confusion

## Future Considerations

- All new endpoints should follow this standardized format
- Consider adding pagination metadata in the `data` object for list endpoints
- Add request/response logging to monitor API usage patterns
- Implement API versioning strategy for future changes
