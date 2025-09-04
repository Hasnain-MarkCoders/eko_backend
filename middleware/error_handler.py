from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

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
    """Handle validation errors and return standardized error format"""
    # Extract the first validation error message
    error_messages = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")
    
    error_message = "; ".join(error_messages) if error_messages else "Validation error"
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": f"Validation error: {error_message}",
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
            "message": "Internal server error",
            "data": None
        }
    )
