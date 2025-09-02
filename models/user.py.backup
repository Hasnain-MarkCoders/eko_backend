from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class UserModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    uid: Optional[str] = None
    email: str
    name: str
    provider: Optional[str] = "email"
    status: str = "active"
    welcome: bool = True
    image: Optional[str] = "https://sauced-app-bucket.s3.us-east-2.amazonodb.net/sauced_placeholder.webp"
    type: str = "user"
    notificationToken: Optional[str] = ""
    isDeleted: bool = False
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "validate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "provider": "email",
                "status": "active",
                "welcome": True,
                "image": "https://example.com/image.jpg",
                "type": "user"
            }
        }
    }

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    provider: str
    status: str
    welcome: bool
    image: str
    type: str
    notificationToken: Optional[str]
    isDeleted: bool
    createdAt: datetime
    updatedAt: datetime 