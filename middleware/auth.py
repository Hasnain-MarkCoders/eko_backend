from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from dotenv import load_dotenv
from database import users
from bson import ObjectId
from locales import get_message
from schemas.enums import Language

load_dotenv()

TOKEN_KEY = os.getenv("TOKEN_KEY", "Test_124")  # Default fallback
security = HTTPBearer()

def get_language_from_request(request: Request) -> str:
    """Get language from request headers or default to English"""
    language = request.headers.get("Accept-Language", "en")[:2]
    if language not in ["en", "fr"]:
        language = "en"
    return language

async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user with language support"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, TOKEN_KEY, algorithms=["HS256"])
        user_id = payload.get("_id")
        
        if user_id is None:
            language = get_language_from_request(request)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=get_message(language, "general.unauthorized"),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validate user_id is a valid ObjectId
        try:
            user_object_id = ObjectId(user_id)
        except Exception:
            language = get_language_from_request(request)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_message(language, "general.invalid_user_id"),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = await users.find_one({"_id": user_object_id})
        
        if user is None:
            language = get_language_from_request(request)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=get_message(language, "general.unauthorized"),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Convert ObjectId to string for response
        user["_id"] = str(user["_id"])
        
        # Get user's language preference and add to request state
        user_language = user.get("language", Language.ENGLISH)
        # Convert language enum to locale code for get_message()
        locale_code = Language.get_locale_code(user_language)
        
        # Add language to request state for use in controllers
        request.state.user_language = locale_code
        
        return user
        
    except jwt.ExpiredSignatureError:
        language = get_language_from_request(request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_message(language, "general.unauthorized"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        language = get_language_from_request(request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_message(language, "general.unauthorized"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        language = get_language_from_request(request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_message(language, "general.unauthorized"),
            headers={"WWW-Authenticate": "Bearer"},
        ) 