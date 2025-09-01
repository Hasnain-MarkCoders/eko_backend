# Eko Backend API

A FastAPI-based backend application with core authentication and profile management features.

## Features

### Authentication
- Firebase authentication for regular users
- JWT token-based session management

### Profile Management
- Change user display name
- Update profile image
- Delete user account
- Check account status
- Get user profile information
- Welcome status management
- Notification token updates

## Prerequisites

- Python 3.11+
- MongoDB database
- Firebase project with service account

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```bash
   MONGO_URI=your_mongodb_connection_string
   TOKEN_KEY=your_jwt_secret_key
   ```

4. Ensure Firebase service account JSON is in the root directory

## Running the Application

### Development
```bash
python app.py
```

### Docker
```bash
docker build -t eko-backend .
docker run -p 8000:8000 eko-backend
```

## API Endpoints

### Authentication
- `POST /auth/firebase` - Firebase authentication

### Profile Management
- `PUT /profile/change-name` - Change user name
- `PUT /profile/change-image` - Update profile image
- `DELETE /profile/delete` - Delete user account
- `GET /profile/is-active` - Check account status
- `GET /profile/user` - Get user profile
- `GET /profile/welcome1` - Check welcome status
- `PUT /profile/welcome2` - Update welcome status
- `PUT /profile/update-token` - Update notification token

## Database Collections

- `users` - User accounts and profiles

## Project Structure

```
eko_backend/
├── app.py                 # Main FastAPI application
├── database.py            # Database connection and setup
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── .env                  # Environment variables
├── models/               # Database models
├── controllers/          # Business logic controllers
├── routes/               # API route definitions
├── schemas/              # Request/response models
├── services/             # External service integrations
└── middleware/           # Authentication middleware
```

## Notes

- AWS S3 integration is currently disabled (credentials not configured)
- The application uses async MongoDB operations for better performance
- JWT tokens expire after 60 days
- Firebase Admin SDK is used for authentication verification
- **No social media features** - focused on core profile management only 