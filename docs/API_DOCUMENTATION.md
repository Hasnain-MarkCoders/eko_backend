# Eko Backend API - Endpoint Documentation

This document provides comprehensive documentation for all available API endpoints in the Eko Backend.

## Base URL

- **Local Development:** `http://localhost:9753`
- **Production:** `https://your-domain.com` (configure as needed)

## Authentication

Most endpoints require authentication via Firebase ID tokens. Include the token in the Authorization header:

```
Authorization: Bearer <firebase_id_token>
```

## Endpoints

### Authentication Endpoints

#### User Registration
```http
POST /auth/signup
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "message": "User created successfully",
  "user": {
    "_id": "user_id",
    "email": "user@example.com",
    "name": "User Name",
    "uid": "firebase_uid"
  }
}
```

#### User Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "_id": "user_id",
    "email": "user@example.com",
    "name": "User Name",
    "uid": "firebase_uid"
  }
}
```

#### Forgot Password
```http
POST /auth/forgot-password
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Password reset email sent successfully"
}
```

#### User Onboarding
```http
POST /auth/onboarding
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "John Doe",
  "age": 25,
  "gender": "male",
  "language": "english",
  "purpose": "personal assistance"
}
```

**Response:**
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
    "welcome": false,
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Field Validation:**
- `name`: Required, non-empty string
- `age`: Required, integer between 1-120
- `gender`: Required, one of: "male", "female", "other"
- `language`: Required, one of: "english", "spanish", "french", "german", "italian", "portuguese", "chinese", "japanese", "korean", "arabic", "hindi"
- `purpose`: Required, one of: "personal assistance", "business", "education", "entertainment", "health", "productivity", "social", "other"

**Error Responses:**
- `400 Bad Request`: User has already completed onboarding (welcome = false)
- `400 Bad Request`: Missing required fields or invalid field values
- `404 Not Found`: User not found
- `500 Internal Server Error`: Firebase or MongoDB update failure

### Profile Management Endpoints

#### Change Display Name
```http
PUT /profile/change-name
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "newName": "New Display Name"
}
```

**Response:**
```json
{
  "message": "User Name Changed Successfully",
  "user": {
    "_id": "user_id",
    "name": "New Display Name",
    "email": "user@example.com",
    "updatedAt": "2024-01-01T00:00:00Z"
  }
}
```

#### Change Profile Image
```http
PUT /profile/change-image
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "image_url": "https://example.com/profile-image.jpg"
}
```

**Response:**
```json
{
  "message": "User Image Changed Successfully",
  "user": {
    "_id": "user_id",
    "name": "User Name",
    "email": "user@example.com",
    "image": "https://example.com/profile-image.jpg",
    "updatedAt": "2024-01-01T00:00:00Z"
  }
}
```

#### Delete User Account
```http
DELETE /profile/delete
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "User account deleted successfully",
  "note": "Account has been deactivated and personal information removed. Firebase account has been deleted."
}
```

#### Check Account Status
```http
GET /profile/is-active
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "status": "active"
}
```

#### Get User Profile
```http
GET /profile/user
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "user": {
    "_id": "user_id",
    "name": "User Name",
    "email": "user@example.com",
    "image": "https://example.com/profile-image.jpg",
    "status": "active",
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z"
  }
}
```

#### Welcome Status Check
```http
GET /profile/welcome1
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Welcome 1"
}
```

#### Update Welcome Status
```http
PUT /profile/welcome2
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Welcome 2",
  "user": {
    "_id": "user_id",
    "name": "User Name",
    "email": "user@example.com",
    "welcome": false,
    "updatedAt": "2024-01-01T00:00:00Z"
  }
}
```

#### Update Notification Token
```http
PUT /profile/update-token
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "notificationToken": "fcm_token_here"
}
```

**Response:**
```json
{
  "message": "Notification Token Updated Successfully",
  "user": {
    "_id": "user_id",
    "name": "User Name",
    "email": "user@example.com",
    "notificationToken": "fcm_token_here",
    "updatedAt": "2024-01-01T00:00:00Z"
  }
}
```

#### Debug Name Comparison
```http
GET /profile/debug-name/{user_id}
```

**Description:** Debug endpoint to compare display names between MongoDB and Firebase

**Parameters:**
- `user_id` (path): The user ID to debug

**Response:**
```json
{
  "mongo": {
    "uid": "firebase_uid",
    "name": "Display Name in MongoDB",
    "email": "user@example.com"
  },
  "firebase": {
    "uid": "firebase_uid",
    "display_name": "Display Name in Firebase"
  }
}
```

### Utility Endpoints

#### API Welcome Message
```http
GET /
```

**Response:**
```json
{
  "message": "Welcome to Eko Backend API"
}
```

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Error description"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Request/Response Schemas

### User Object
```json
{
  "_id": "string",
  "name": "string",
  "email": "string",
  "image": "string",
  "uid": "string",
  "status": "string",
  "welcome": "boolean",
  "notificationToken": "string",
  "isDeleted": "boolean",
  "age": "integer",
  "gender": "string",
  "language": "string",
  "purpose": "string",
  "createdAt": "string (ISO 8601)",
  "updatedAt": "string (ISO 8601)",
  "deletedAt": "string (ISO 8601)"
}
```

### Error Object
```json
{
  "detail": "string"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## CORS

CORS is configured to allow all origins (`*`) for development. Configure specific origins for production.

## Testing

Use the provided Postman collection (`Eko_Backend_API.postman_collection.json`) for testing endpoints.

## Notes

- All timestamps are in ISO 8601 format with UTC timezone
- User IDs are MongoDB ObjectIds converted to strings
- Firebase UIDs are used for authentication and cross-platform user identification
- The debug endpoint is for development purposes and should be removed or secured in production
