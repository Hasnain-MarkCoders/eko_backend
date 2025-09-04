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

## Internationalization (i18n)

The API supports multiple languages for all response messages. Language detection works as follows:

### Language Detection Priority:
1. **User's stored language preference** (for authenticated endpoints)
2. **Accept-Language header** (for unauthenticated endpoints)
3. **Default to English** (fallback)

### Supported Languages:
- `en` - English (default)
- `fr` - French

### Language Headers:
For unauthenticated endpoints, include the language preference in the request header:
```
Accept-Language: fr
```

### Example Localized Responses:

**English Response:**
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {...}
}
```

**French Response:**
```json
{
  "success": true,
  "message": "Utilisateur créé avec succès",
  "data": {...}
}
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
  "password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!",
  "language": "en",
  "agreed": true
}
```

**Field Validation:**
- `email`: Valid email address (required)
- `password`: Minimum 8 characters (required)
- `confirm_password`: Must match password exactly (required)
- `language`: Must be "en" or "fr" (default: "en")
- `agreed`: Must be true (required)

**Response:**
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "user_id": "user_id",
    "uid": "firebase_uid",
    "email": "user@example.com",
    "name": "",
    "provider": "password",
    "status": "active",
    "welcome": true,
    "image": "https://sauced-app-bucket.s3.us-east-2.amazonaws.com/sauced_placeholder.webp",
    "type": "user",
    "notificationToken": "",
    "isDeleted": false,
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error Responses:**

**Passwords Don't Match:**
```json
{
  "success": false,
  "message": "Passwords do not match",
  "data": null
}
```

**Must Agree to Privacy Policy:**
```json
{
  "success": false,
  "message": "You must agree to the privacy policy to continue",
  "data": null
}
```

**Email Already Exists:**
```json
{
  "success": false,
  "message": "User with this email already exists",
  "data": null
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
  "success": true,
  "message": "Login successful",
  "data": {
    "user_id": "user_id",
    "uid": "firebase_uid",
    "email": "user@example.com",
    "name": "User Name",
    "provider": "password",
    "status": "active",
    "welcome": true,
    "image": "https://sauced-app-bucket.s3.us-east-2.amazonaws.com/sauced_placeholder.webp",
    "type": "user",
    "notificationToken": "",
    "isDeleted": false,
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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
  "success": true,
  "message": "Password reset email sent successfully",
  "data": {
    "resetLink": "https://example.com/reset?token=...",
    "note": "In production, this link would be sent via email"
  }
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
  "language": "en",
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
- `language`: Required, one of: "en", "fr"
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
  "success": true,
  "message": "User Name Changed Successfully",
  "data": {
    "user_id": "user_id",
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
  "success": true,
  "message": "User Image Changed Successfully",
  "data": {
    "user_id": "user_id",
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
  "success": true,
  "message": "User account deleted successfully",
  "data": {
    "note": "Account has been deactivated and personal information removed. Firebase account has been deleted."
  }
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
  "success": true,
  "message": "User status retrieved successfully",
  "data": {
    "status": "active"
  }
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
  "success": true,
  "message": "User profile retrieved successfully",
  "data": {
    "user_id": "user_id",
    "name": "User Name",
    "email": "user@example.com",
    "image": "https://example.com/profile-image.jpg",
    "status": "active",
    "welcome": true,
    "notificationToken": "",
    "age": 25,
    "gender": "male",
    "language": "english",
    "purpose": "personal assistance",
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
  "success": true,
  "message": "Welcome 1",
  "data": null
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
  "success": true,
  "message": "Welcome 2",
  "data": {
    "user_id": "user_id",
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
  "success": true,
  "message": "Notification Token Updated Successfully",
  "data": {
    "user_id": "user_id",
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
  "success": true,
  "message": "Name comparison retrieved successfully",
  "data": {
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
}
```

### Chat Management Endpoints

#### Get Chat Suggestions
```http
GET /chat/suggestions
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "Chat suggestions retrieved successfully",
  "data": [
    {"title": "Help with coding", "value": "coding_help"},
    {"title": "Mental health support", "value": "mental_health"},
    {"title": "General conversation", "value": "general_chat"},
    {"title": "Learning assistance", "value": "learning_help"},
    {"title": "Problem solving", "value": "problem_solving"}
  ]
}
```

#### Get Saved Chats
```http
GET /chat/saved
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "Saved chats retrieved successfully",
  "data": [
    {
      "chat_id": "68ba031cda9127adb68239a8",
      "title": "Test Chat",
      "short_description": "Testing message functionality"
    }
  ]
}
```

#### Create New Chat
```http
POST /chat/create
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "New Programming Discussion",
  "short_description": "Help with JavaScript concepts",
  "is_temporary": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Chat created successfully",
  "data": {
    "chatId": "68ba031cda9127adb68239a8",
    "title": "New Programming Discussion",
    "short_description": "Help with JavaScript concepts",
    "is_temporary": false,
    "status": "active",
    "createdAt": "2025-09-04T21:22:36.622858Z",
    "updatedAt": "2025-09-04T21:22:36.622865Z",
    "lastMessageAt": "2025-09-04T21:22:36.622868Z",
    "messageCount": 0,
    "isDeleted": false
  }
}
```

#### Delete Specific Chat
```http
DELETE /chat/{chat_id}
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "Chat deleted successfully",
  "data": {
    "chatId": "68ba031cda9127adb68239a8",
    "deletedAt": "2025-09-04T21:22:36.622858Z"
  }
}
```

#### Delete All User Chats
```http
DELETE /chat/all
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "All chats deleted successfully",
  "data": {
    "deletedCount": 2,
    "deletedAt": "2025-09-04T21:22:36.622858Z"
  }
}
```

### Message Management Endpoints

#### Get Conversation Messages
```http
GET /chat/{chat_id}/messages?page=1&limit=20
```

**Headers:** `Authorization: Bearer <token>`

**Parameters:**
- `chat_id` (path): The chat ID to get messages from
- `page` (query): Page number (default: 1)
- `limit` (query): Number of messages per page (default: 20, max: 100)

**Response:**
```json
{
  "success": true,
  "message": "Conversation retrieved successfully",
  "data": {
    "messages": [
      {
        "messageId": "68ba0326da9127adb68239aa",
        "chatId": "68ba031cda9127adb68239a8",
        "userId": "68b8e928f9872144cc79cf59",
        "sender": "bot",
        "message": "Of course, I'm here to help. I'm sorry to hear you're feeling stressed...",
        "pictures": [],
        "voices": [],
        "timestamp": "2025-09-04T21:22:46.349000Z",
        "isDeleted": false,
        "updatedAt": "2025-09-04T21:22:46.349000Z"
      },
      {
        "messageId": "68ba0323da9127adb68239a9",
        "chatId": "68ba031cda9127adb68239a8",
        "userId": "68b8e928f9872144cc79cf59",
        "sender": "user",
        "message": "Hello EKO, I am feeling stressed today. Can you help me?",
        "pictures": [],
        "voices": [],
        "timestamp": "2025-09-04T21:22:43.683000Z",
        "isDeleted": false,
        "updatedAt": "2025-09-04T21:22:43.683000Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 1,
      "total_messages": 2,
      "has_next": false
    }
  }
}
```

#### Send Message to EKO Bot
```http
POST /chat/{chat_id}/message
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "message": "Hello EKO, I am feeling stressed today. Can you help me?",
  "pictures": [],
  "voices": []
}
```

**Response:**
```json
{
  "success": true,
  "message": "Message sent successfully",
  "data": {
    "messageId": "68ba0323da9127adb68239a9",
    "chatId": "68ba031cda9127adb68239a8",
    "sender": "user",
    "message": "Hello EKO, I am feeling stressed today. Can you help me?",
    "pictures": [],
    "voices": [],
    "timestamp": "2025-09-04T21:22:43.683252Z",
    "bot_response": {
      "messageId": "68ba0326da9127adb68239aa",
      "chatId": "68ba031cda9127adb68239a8",
      "sender": "bot",
      "message": "Of course, I'm here to help. I'm sorry to hear you're feeling stressed. Would you like to talk about what's been causing you stress or how it's been affecting you today?",
      "pictures": [],
      "voices": [],
      "timestamp": "2025-09-04T21:22:46.349692Z"
    }
  }
}
```

#### Update Message
```http
PUT /message/{message_id}
```

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "message": "Updated message content",
  "pictures": ["new_image_url"],
  "voices": ["new_voice_url"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Message updated successfully",
  "data": {
    "messageId": "68ba0323da9127adb68239a9",
    "updated_message": "Updated message content",
    "pictures": ["new_image_url"],
    "voices": ["new_voice_url"],
    "updated_at": "2025-09-04T21:22:50.123456Z"
  }
}
```

#### Delete Message
```http
DELETE /message/{message_id}
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "Message deleted successfully",
  "data": {
    "deleted_message_id": "68ba0323da9127adb68239a9"
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
  "success": true,
  "message": "Welcome to Eko Backend API",
  "data": null
}
```

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "success": true,
  "message": "API is healthy",
  "data": {
    "status": "healthy"
  }
}
```

## Error Responses

All endpoints return standardized error responses in the following format:

### Standard Error Response Format
```json
{
  "success": false,
  "message": "Error description",
  "data": null
}
```

### Common Error Responses

#### 400 Bad Request
```json
{
  "success": false,
  "message": "Error description",
  "data": null
}
```

#### 401 Unauthorized
```json
{
  "success": false,
  "message": "Invalid or expired token",
  "data": null
}
```

#### 404 Not Found
```json
{
  "success": false,
  "message": "Resource not found",
  "data": null
}
```

#### 422 Validation Error
```json
{
  "success": false,
  "message": "Validation error: field_name: error description",
  "data": null
}
```

#### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Internal server error",
  "data": null
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
  "success": false,
  "message": "string",
  "data": null
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
