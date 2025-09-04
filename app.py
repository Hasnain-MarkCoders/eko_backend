from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from routes import auth, profile
from middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from middleware.auth import get_language_from_request
from locales import get_message
import uvicorn

app = FastAPI(
    title="Eko Backend API",
    description="Backend API for Eko application with authentication and profile management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers for standardized error responses
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(auth.router)
app.include_router(profile.router)

@app.get("/")
async def root(request: Request):
    language = get_language_from_request(request)
    return {
        "success": True,
        "message": get_message(language, "general.welcome"),
        "data": None
    }

@app.get("/health")
async def health_check(request: Request):
    language = get_language_from_request(request)
    return {
        "success": True,
        "message": get_message(language, "general.health"),
        "data": {
            "status": "healthy"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
