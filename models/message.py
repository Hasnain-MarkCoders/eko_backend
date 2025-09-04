from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

class MessageModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    chatId: str = Field(..., description="Reference to chat ID")
    userId: str = Field(..., description="Reference to user ID")
    sender: str = Field(..., description="Message sender: user, bot, system")
    message: str = Field(..., description="Message content")
    pictures: List[str] = Field(default=[], description="Array of picture URLs")
    voices: List[str] = Field(default=[], description="Array of voice URLs")
    timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    isDeleted: bool = Field(default=False, description="Soft delete flag")
    updatedAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "validate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "chatId": "507f1f77bcf86cd799439011",
                "userId": "507f1f77bcf86cd799439012",
                "sender": "user",
                "message": "Hello, can you help me with JavaScript?",
                "pictures": [],
                "voices": []
            }
        }
    }

class MessageResponse(BaseModel):
    messageId: str
    chatId: str
    userId: str
    sender: str
    message: str
    pictures: List[str]
    voices: List[str]
    timestamp: datetime
    isDeleted: bool
    updatedAt: datetime

class SendMessageRequest(BaseModel):
    message: str = Field(..., description="Message content")
    pictures: List[str] = Field(default=[], description="Array of picture URLs")
    voices: List[str] = Field(default=[], description="Array of voice URLs")

class UpdateMessageRequest(BaseModel):
    message: str = Field(..., description="Updated message content")
    pictures: List[str] = Field(default=[], description="Array of picture URLs")
    voices: List[str] = Field(default=[], description="Array of voice URLs")

class ConversationResponse(BaseModel):
    messages: List[MessageResponse]
    pagination: dict

class SendMessageResponse(BaseModel):
    messageId: str
    chatId: str
    sender: str
    message: str
    pictures: List[str]
    voices: List[str]
    timestamp: datetime
    bot_response: Optional[MessageResponse] = None

class UpdateMessageResponse(BaseModel):
    messageId: str
    updated_message: str
    pictures: List[str]
    voices: List[str]
    updated_at: datetime

class DeleteMessageResponse(BaseModel):
    deleted_message_id: str
