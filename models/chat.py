from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class ChatModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    userId: str = Field(..., description="Reference to user ID")
    title: str = Field(..., description="Chat title")
    short_description: str = Field(..., description="Short description of the chat")
    is_temporary: bool = Field(default=False, description="Whether the chat is temporary")
    status: str = Field(default="active", description="Chat status: active, archived, deleted")
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    lastMessageAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    messageCount: int = Field(default=0, description="Total messages in chat")
    isDeleted: bool = Field(default=False, description="Soft delete flag")

    model_config = {
        "validate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "userId": "507f1f77bcf86cd799439011",
                "title": "New Programming Discussion",
                "short_description": "Help with JavaScript concepts",
                "is_temporary": False,
                "status": "active",
                "messageCount": 0
            }
        }
    }

class ChatResponse(BaseModel):
    chatId: str
    title: str
    short_description: str
    is_temporary: bool
    status: str
    createdAt: datetime
    updatedAt: datetime
    lastMessageAt: datetime
    messageCount: int
    isDeleted: bool

class CreateChatRequest(BaseModel):
    title: str = Field(..., description="Chat title")
    short_description: str = Field(..., description="Short description of the chat")
    is_temporary: bool = Field(..., description="Whether the chat is temporary")

class DeleteChatResponse(BaseModel):
    chatId: str
    deletedAt: datetime

class DeleteAllChatsResponse(BaseModel):
    deletedCount: int
    deletedAt: datetime
