# Task 1: User Onboarding Endpoint

## Overview
Create a new onboarding endpoint that will be called after the user signup API to collect additional user information during the registration flow.

## Endpoint Details

### Request
```http
POST /auth/onboarding
```

### Request Body
```json
{
    "name": "John Doe",
    "age": 25,
    "gender": "male",
    "language": "english",
    "purpose": "personal assistance"
}
```

### Response
```json
{
    "success": true,
    "message": "Onboarding completed successfully",
    "data": {
        "user_id": "12345",
        "name": "John Doe",
        "email": "user@example.com",
        "age": 25,
        "gender": "male",
        "language": "english",
        "purpose": "personal assistance",
        "profile_completed": true,
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

## Implementation Requirements

### 1. Database Schema Updates
Update the user model in `models/user.py` to include the new fields:
- `age` (integer)
- `gender` (string)
- `language` (string) 
- `purpose` (string)
- `profile_completed` (boolean, default: false)

### 2. Firebase Integration
**IMPORTANT**: The `name` field must be updated in Firebase as well, similar to how the `profile/change-name` API works. This ensures consistency between MongoDB and Firebase.

### 3. Controller Implementation
Create a new method in `controllers/auth_controller.py`:
- `onboarding()` method to handle the onboarding logic
- **Check if `profile_completed` is already true** - if so, return error (400 Bad Request)
- Validate all required fields
- Update both MongoDB and Firebase
- Set `profile_completed` to `true` after successful onboarding
- Return updated user data with auth token

### 4. Schema Definition
Create request/response schemas in `schemas/auth.py`:
- `OnboardingRequest` schema for input validation
- Include proper field validation (required fields, data types)

### 5. Route Implementation
Add the new route in `routes/auth.py`:
- `POST /auth/onboarding` endpoint
- Include proper authentication middleware
- Handle errors appropriately

## Field Specifications

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | User's display name |
| `age` | integer | Yes | User's age |
| `gender` | string | Yes | User's gender |
| `language` | string | Yes | User's preferred language |
| `purpose` | string | Yes | User's purpose for using the app |

### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Indicates if the request was successful |
| `message` | string | Success/error message |
| `data.user_id` | string | User's unique identifier |
| `data.name` | string | User's display name |
| `data.email` | string | User's email address |
| `data.age` | integer | User's age |
| `data.gender` | string | User's gender |
| `data.language` | string | User's preferred language |
| `data.purpose` | string | User's purpose for using the app |
| `data.profile_completed` | boolean | Indicates if user has completed onboarding |
| `data.token` | string | JWT token for authentication |

## Validation Rules

- All fields are required
- `name` must not be empty
- `age` must be a positive integer
- `gender` should be validated against allowed values (e.g., "male", "female", "other")
- `language` should be validated against supported languages
- `purpose` should be validated against allowed purposes

## Error Handling

Handle the following error cases:
- Missing required fields (400 Bad Request)
- Invalid field values (400 Bad Request)
- **Profile already completed** (400 Bad Request) - User has already completed onboarding
- User not found (404 Not Found)
- Firebase update failure (500 Internal Server Error)
- MongoDB update failure (500 Internal Server Error)

## Testing

Create test cases for:
- Successful onboarding with valid data
- **Profile already completed error** - User tries to onboard when already completed
- Validation errors for missing fields
- Validation errors for invalid field values
- Firebase integration testing
- MongoDB update verification
- Auth token generation and return

## Dependencies

This task requires:
- Existing authentication system
- Firebase Admin SDK integration
- MongoDB user model
- Current user authentication middleware

## Notes

- This endpoint should be called after successful signup
- The user must be authenticated (include auth middleware)
- Ensure data consistency between MongoDB and Firebase
- Consider adding field validation for gender, language, and purpose values
- Update API documentation after implementation
