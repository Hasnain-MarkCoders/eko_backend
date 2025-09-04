from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
from locales import get_message
from middleware.auth import get_language_from_request

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions and return standardized error format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": None
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors and return standardized error format with localized messages"""
    # Get language from request headers
    language = get_language_from_request(request)
    
    # Extract the first validation error message
    error_messages = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        
        # Map Pydantic validation errors to localized messages
        if "Passwords do not match" in message:
            localized_message = get_message(language, "auth.signup.passwords_no_match")
        elif "You must agree to the privacy policy to continue" in message:
            localized_message = get_message(language, "auth.signup.must_agree")
        elif "ensure this value has at least" in message and "characters" in message:
            localized_message = get_message(language, "auth.signup.weak_password")
        elif "invalid choice" in message.lower():
            localized_message = get_message(language, "auth.signup.invalid_language")
        else:
            localized_message = message  # Fallback to original message
        
        error_messages.append(f"{field}: {localized_message}")
    
    error_message = "; ".join(error_messages) if error_messages else get_message(language, "general.validation_error")
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": error_message,
            "data": None
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions and return standardized error format"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",  # Default English for unhandled errors
            "data": None
        }
    )
