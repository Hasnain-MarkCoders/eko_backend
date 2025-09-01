from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, profile
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

# Include routers
app.include_router(auth.router)
app.include_router(profile.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Eko Backend API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
