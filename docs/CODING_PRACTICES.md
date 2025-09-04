# Eko Backend - Coding Practices & Standards

This document outlines the coding practices, standards, and conventions we follow in the Eko Backend project. All developers should adhere to these practices to maintain consistency, quality, and maintainability.

## 🎯 Core Principles

### 1. **Standardized API Response Format**
**ALWAYS** use the standardized response format for ALL endpoints:

```json
{
  "success": boolean,
  "message": string,
  "data": object | array | null
}
```

**✅ DO:**
```python
return {
    "success": True,
    "message": get_message(language, "auth.signup.success"),
    "data": {
        "user_id": str(result.inserted_id),
        "email": user["email"]
    }
}
```

**❌ DON'T:**
```python
return {"user": user_data}  # Inconsistent format
return {"message": "Success"}  # Missing success and data fields
```

### 2. **Internationalization (i18n) - NO HARDCODED MESSAGES**
**NEVER** hardcode English messages. ALL messages must be localized.

**✅ DO:**
```python
# Use get_message() for all user-facing messages
message = get_message(language, "auth.signup.success")
detail = get_message(language, "auth.signup.email_exists")
```

**❌ DON'T:**
```python
# Never hardcode English messages
message = "User created successfully"  # Hardcoded English
detail = "User with this email already exists"  # Hardcoded English
```

### 3. **Language Handling**
- **Signup API**: Use language from request body (new users don't exist in DB yet)
- **All other APIs**: Use user's stored language preference from database
- **Request Language**: Frontend sends `"EN"` or `"FR"` in request bodies
- **Database Language**: Stored as `"english"` or `"french"` in database
- **Language Conversion**: Use `LanguageRequest.to_database_language()` to convert request to database format
- **Locale conversion**: Use `Language.get_locale_code()` for get_message()

## 🏗️ Development Environment

### **Docker-Only Development**
**ALWAYS** use Docker for development. Never run the backend directly on your machine.

**✅ DO:**
```bash
# First time setup or fresh deployment
./deploy.sh

# After git pull or code changes (faster rebuild)
./restart.sh

# Non-interactive mode for production
./deploy.sh -y
./restart.sh -y
```

**❌ DON'T:**
```bash
# Never run directly on local machine
python app.py  # Wrong!
uvicorn app:app --reload  # Wrong!
```

### **Deployment Script Usage**

#### **deploy.sh** - Initial Setup
- **Purpose**: First-time deployment or fresh setup
- **What it does**: Builds image from scratch, creates container
- **When to use**: New environment, major changes, or first deployment

#### **restart.sh** - Fast Redeploy  
- **Purpose**: Quick redeploy after code changes
- **What it does**: Stops container, rebuilds with cache, restarts
- **When to use**: After `git pull`, code changes, or regular updates
- **Docker Compose Question**: When asked "Use docker-compose?", say **NO** for faster deployment (avoids reinstalling dependencies from scratch)

**✅ Recommended Workflow:**
```bash
# Development cycle
git pull
./restart.sh  # Say NO to docker-compose for speed
# Test your changes
git commit -m "Your changes"
git push
```

## 📁 Project Structure Standards

### **File Organization**
```
eko_backend/
├── app.py                 # Main FastAPI application
├── controllers/           # Business logic
├── routes/               # API route definitions
├── schemas/              # Pydantic models and enums
├── middleware/           # Custom middleware
├── services/             # External service integrations
├── locales/              # Internationalization files
├── docs/                 # Documentation
└── database.py           # Database connection
```

### **Import Order**
```python
# 1. Standard library imports
import os
from datetime import datetime

# 2. Third-party imports
from fastapi import HTTPException
from pydantic import BaseModel

# 3. Local imports
from database import users
from locales import get_message
from schemas.enums import Language, LanguageRequest
```

### **Language Enums Usage**
```python
# For request bodies (signup, onboarding)
from schemas.enums import LanguageRequest

# Convert request language to database language
database_language = LanguageRequest.to_database_language("EN")  # Returns "english"
database_language = LanguageRequest.to_database_language("FR")  # Returns "french"

# For database operations and existing users
from schemas.enums import Language

# Convert database language to locale code for get_message()
locale_code = Language.get_locale_code("english")  # Returns "en"
locale_code = Language.get_locale_code("french")   # Returns "fr"
```

## 🔧 API Development Standards

### **Controller Method Signatures**
```python
# For authenticated endpoints (user exists in DB)
async def method_name(self, user_id: str, param1: str, user_language: str = "en"):
    """Method description - uses user's stored language preference"""

# For unauthenticated endpoints (signup, login)
async def method_name(self, param1: str, param2: str, request_language: str = "en"):
    """Method description - uses request language from headers"""
```

### **Error Handling**
```python
try:
    # Business logic
    result = await some_operation()
    return {
        "success": True,
        "message": get_message(language, "operation.success"),
        "data": result
    }
except HTTPException:
    # Re-raise HTTPExceptions to preserve their localized messages
    raise
except Exception as error:
    # Handle unexpected errors
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=get_message(language, "general.internal_error")
    )
```

### **Route Definitions**
```python
@router.post("/endpoint", response_model=StandardResponse)
async def endpoint_name(request: RequestSchema, current_user: dict = Depends(get_current_user), http_request: Request = None):
    """Endpoint description"""
    # Get user's language preference from request state
    user_language = getattr(http_request.state, 'user_language', 'en')
    return await controller.method_name(current_user["_id"], request.param, user_language)
```

## 🌍 Internationalization Standards

### **Locale File Structure**
```json
{
  "auth": {
    "signup": {
      "success": "User created successfully",
      "email_exists": "User with this email already exists"
    }
  },
  "general": {
    "internal_error": "Internal server error",
    "validation_error": "Validation error"
  }
}
```

### **Message Key Naming**
- Use dot notation: `category.action.result`
- Examples: `auth.signup.success`, `profile.change_name.user_not_found`
- Keep keys descriptive and consistent

### **Adding New Messages**
1. Add to both `locales/en.json` and `locales/fr.json`
2. Use consistent key naming
3. Test both languages
4. Update API documentation

## 📝 Documentation Standards

### **API Documentation**
- Update `docs/API_DOCUMENTATION.md` for all endpoint changes
- Include request/response examples
- Show error response examples
- Document field validation rules

### **Code Comments**
```python
async def method_name(self, param: str):
    """Brief description of what this method does
    
    Args:
        param: Description of parameter
        
    Returns:
        StandardResponse: Description of return value
        
    Raises:
        HTTPException: When specific error occurs
    """
```

## 🧪 Testing Standards

### **Before Committing**
1. Test all endpoints with both English and French
2. Verify error messages are localized
3. Check response format consistency
4. Test validation error scenarios
5. Run in Docker environment

### **Test Scenarios**
- Valid requests (both languages)
- Invalid requests (validation errors)
- Error conditions (user not found, etc.)
- Authentication scenarios

## 🚀 Deployment Standards

### **Environment Variables**
- Never commit `.env` files
- Use environment variables for all configuration
- Document required environment variables

### **Docker Configuration**
- Always use `docker-compose.yml` for local development
- Use `deploy.sh` script for deployment
- Keep Dockerfile optimized and secure

## 🔒 Security Standards

### **Authentication**
- Use JWT tokens for session management
- Validate all input data with Pydantic
- Never expose sensitive information in responses

### **Data Validation**
- Use Pydantic schemas for all request/response validation
- Implement proper error handling
- Sanitize all user inputs

## 📋 Code Review Checklist

Before submitting code for review, ensure:

- [ ] All responses use standardized format
- [ ] No hardcoded English messages
- [ ] Proper error handling with localized messages
- [ ] Updated API documentation
- [ ] Added/updated locale files if needed
- [ ] Tested in Docker environment
- [ ] Follows import order standards
- [ ] Proper method signatures
- [ ] Consistent naming conventions

## 🎯 Future Considerations

### **Pagination**
When implementing paginated endpoints, use this structure:
```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 150,
    "total_pages": 15,
    "has_next": true,
    "has_prev": false
  }
}
```

### **Adding New Languages**
1. Create new locale file (e.g., `locales/es.json`)
2. Update Language enum
3. Update `get_locale_code()` method
4. Test all endpoints with new language

---

**Remember**: Consistency is key. Follow these practices religiously to maintain code quality and team productivity.
