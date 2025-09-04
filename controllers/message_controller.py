from fastapi import HTTPException, status
from database import messages, chats, users
from services.openai import OpenAIService
from models.message import (
    MessageModel, MessageResponse, SendMessageRequest, UpdateMessageRequest,
    ConversationResponse, SendMessageResponse, UpdateMessageResponse, DeleteMessageResponse
)
from bson import ObjectId
from datetime import datetime, timezone
from locales import get_message
from schemas.enums import Language

class MessageController:
    def __init__(self):
        self.openai_service = OpenAIService()
    
    async def get_conversation_messages(self, user_id: str, chat_id: str, page: int = 1, limit: int = 20, user_language: str = "en"):
        """Get paginated messages from a chat conversation"""
        try:
            # Convert string user_id to ObjectId
            try:
                user_object_id = ObjectId(user_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(user_language, "general.invalid_user_id")
                )
            
            # Convert string chat_id to ObjectId
            try:
                chat_object_id = ObjectId(chat_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(user_language, "general.invalid_chat_id")
                )
            
            # Verify user exists
            user = await users.find_one({"_id": user_object_id, "isDeleted": False})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(user_language, "auth.login.user_not_found")
                )
            
            # Verify chat exists and belongs to user
            chat = await chats.find_one({
                "_id": chat_object_id,
                "userId": str(user_object_id),
                "isDeleted": False
            })
            if not chat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(user_language, "chat.not_found")
                )
            
            # Calculate pagination
            skip = (page - 1) * limit
            
            # Get messages with pagination
            messages_cursor = messages.find({
                "chatId": str(chat_object_id),
                "isDeleted": False
            }).sort("timestamp", -1).skip(skip).limit(limit)
            
            messages_list = await messages_cursor.to_list(length=limit)
            
            # Get total count for pagination
            total_messages = await messages.count_documents({
                "chatId": str(chat_object_id),
                "isDeleted": False
            })
            
            # Format messages
            formatted_messages = []
            for msg in messages_list:
                formatted_messages.append({
                    "messageId": str(msg["_id"]),
                    "chatId": msg["chatId"],
                    "userId": msg["userId"],
                    "sender": msg["sender"],
                    "message": msg["message"],
                    "pictures": msg.get("pictures", []),
                    "voices": msg.get("voices", []),
                    "timestamp": msg["timestamp"],
                    "isDeleted": msg.get("isDeleted", False),
                    "updatedAt": msg.get("updatedAt", msg["timestamp"])
                })
            
            # Calculate pagination info
            total_pages = (total_messages + limit - 1) // limit
            has_next = page < total_pages
            
            return {
                "success": True,
                "message": get_message(user_language, "message.conversation.success"),
                "data": {
                    "messages": formatted_messages,
                    "pagination": {
                        "current_page": page,
                        "total_pages": total_pages,
                        "total_messages": total_messages,
                        "has_next": has_next
                    }
                }
            }
            
        except HTTPException:
            raise
        except Exception as error:
            print(f"ERROR getting conversation messages: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_message(user_language, "general.internal_error")
            )
    
    async def send_message(self, user_id: str, chat_id: str, request: SendMessageRequest, user_language: str = "en"):
        """Send a message to the chatbot and get bot response"""
        try:
            # Convert string user_id to ObjectId
            try:
                user_object_id = ObjectId(user_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(user_language, "general.invalid_user_id")
                )
            
            # Convert string chat_id to ObjectId
            try:
                chat_object_id = ObjectId(chat_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(user_language, "general.invalid_chat_id")
                )
            
            # Verify user exists
            user = await users.find_one({"_id": user_object_id, "isDeleted": False})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(user_language, "auth.login.user_not_found")
                )
            
            # Verify chat exists and belongs to user
            chat = await chats.find_one({
                "_id": chat_object_id,
                "userId": str(user_object_id),
                "isDeleted": False
            })
            if not chat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(user_language, "chat.not_found")
                )
            
            now = datetime.now(timezone.utc)
            
            # Create user message
            user_message = {
                "chatId": str(chat_object_id),
                "userId": str(user_object_id),
                "sender": "user",
                "message": request.message.strip(),
                "pictures": request.pictures,
                "voices": request.voices,
                "timestamp": now,
                "isDeleted": False,
                "updatedAt": now
            }
            
            # Insert user message
            user_msg_result = await messages.insert_one(user_message)
            user_message_id = str(user_msg_result.inserted_id)
            
            # Generate bot response
            bot_response = await self._generate_bot_response(
                chat_id=str(chat_object_id),
                user_id=str(user_object_id),
                user_message=request.message.strip(),
                user_language=user.get("language", "english")
            )
            
            # Update chat's last message time and message count
            await chats.update_one(
                {"_id": chat_object_id},
                {
                    "$set": {
                        "lastMessageAt": now,
                        "updatedAt": now
                    },
                    "$inc": {"messageCount": 1 if not bot_response else 2}  # +1 for user message, +1 for bot response
                }
            )
            
            # Format response
            response_data = {
                "messageId": user_message_id,
                "chatId": str(chat_object_id),
                "sender": "user",
                "message": request.message.strip(),
                "pictures": request.pictures,
                "voices": request.voices,
                "timestamp": now
            }
            
            if bot_response:
                response_data["bot_response"] = bot_response
            
            return {
                "success": True,
                "message": get_message(user_language, "message.send.success"),
                "data": response_data
            }
            
        except HTTPException:
            raise
        except Exception as error:
            print(f"ERROR sending message: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_message(user_language, "general.internal_error")
            )
    
    async def _generate_bot_response(self, chat_id: str, user_id: str, user_message: str, user_language: str = "english"):
        """Generate EKO bot response using OpenAI"""
        try:
            # Get recent conversation context (last 10 messages)
            recent_messages = await messages.find({
                "chatId": chat_id,
                "isDeleted": False
            }).sort("timestamp", -1).limit(10).to_list(length=10)
            
            # Build conversation context
            conversation_context = []
            for msg in reversed(recent_messages):  # Reverse to get chronological order
                role = "user" if msg["sender"] == "user" else "assistant"
                conversation_context.append({
                    "role": role,
                    "content": msg["message"]
                })
            
            # Add current user message
            conversation_context.append({
                "role": "user",
                "content": user_message
            })
            
            # Generate bot response using OpenAI
            bot_message = await self.openai_service.generate_bot_response(
                conversation_context, user_language
            )
            
            if bot_message:
                # Create bot message
                now = datetime.now(timezone.utc)
                bot_message_doc = {
                    "chatId": chat_id,
                    "userId": user_id,
                    "sender": "bot",
                    "message": bot_message,
                    "pictures": [],
                    "voices": [],
                    "timestamp": now,
                    "isDeleted": False,
                    "updatedAt": now
                }
                
                # Insert bot message
                bot_msg_result = await messages.insert_one(bot_message_doc)
                
                return {
                    "messageId": str(bot_msg_result.inserted_id),
                    "chatId": chat_id,
                    "sender": "bot",
                    "message": bot_message,
                    "pictures": [],
                    "voices": [],
                    "timestamp": now
                }
            
            return None
            
        except Exception as error:
            print(f"ERROR generating bot response: {error}")
            return None
    
    async def update_message(self, user_id: str, message_id: str, request: UpdateMessageRequest, user_language: str = "en"):
        """Update a specific message"""
        try:
            # Convert string user_id to ObjectId
            try:
                user_object_id = ObjectId(user_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(user_language, "general.invalid_user_id")
                )
            
            # Convert string message_id to ObjectId
            try:
                message_object_id = ObjectId(message_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(user_language, "general.invalid_message_id")
                )
            
            # Verify user exists
            user = await users.find_one({"_id": user_object_id, "isDeleted": False})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(user_language, "auth.login.user_not_found")
                )
            
            # Find and verify message belongs to user
            message = await messages.find_one({
                "_id": message_object_id,
                "userId": str(user_object_id),
                "isDeleted": False
            })
            
            if not message:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(user_language, "message.not_found")
                )
            
            # Update message
            now = datetime.now(timezone.utc)
            result = await messages.update_one(
                {"_id": message_object_id},
                {
                    "$set": {
                        "message": request.message.strip(),
                        "pictures": request.pictures,
                        "voices": request.voices,
                        "updatedAt": now
                    }
                }
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=get_message(user_language, "general.internal_error")
                )
            
            return {
                "success": True,
                "message": get_message(user_language, "message.update.success"),
                "data": {
                    "messageId": message_id,
                    "updated_message": request.message.strip(),
                    "pictures": request.pictures,
                    "voices": request.voices,
                    "updated_at": now
                }
            }
            
        except HTTPException:
            raise
        except Exception as error:
            print(f"ERROR updating message: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_message(user_language, "general.internal_error")
            )
    
    async def delete_message(self, user_id: str, message_id: str, user_language: str = "en"):
        """Delete a specific message (soft delete)"""
        try:
            # Convert string user_id to ObjectId
            try:
                user_object_id = ObjectId(user_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(user_language, "general.invalid_user_id")
                )
            
            # Convert string message_id to ObjectId
            try:
                message_object_id = ObjectId(message_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(user_language, "general.invalid_message_id")
                )
            
            # Verify user exists
            user = await users.find_one({"_id": user_object_id, "isDeleted": False})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(user_language, "auth.login.user_not_found")
                )
            
            # Find and verify message belongs to user
            message = await messages.find_one({
                "_id": message_object_id,
                "userId": str(user_object_id),
                "isDeleted": False
            })
            
            if not message:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(user_language, "message.not_found")
                )
            
            # Soft delete the message
            now = datetime.now(timezone.utc)
            result = await messages.update_one(
                {"_id": message_object_id},
                {
                    "$set": {
                        "isDeleted": True,
                        "updatedAt": now
                    }
                }
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=get_message(user_language, "general.internal_error")
                )
            
            return {
                "success": True,
                "message": get_message(user_language, "message.delete.success"),
                "data": {
                    "deleted_message_id": message_id
                }
            }
            
        except HTTPException:
            raise
        except Exception as error:
            print(f"ERROR deleting message: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_message(user_language, "general.internal_error")
            )
