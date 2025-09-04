from pydantic import BaseModel
from typing import Any, Optional

class StandardResponse(BaseModel):
    """Standard response format for all API endpoints"""
    success: bool
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    """Standard error response format"""
    success: bool = False
    message: str
    data: Optional[Any] = None
