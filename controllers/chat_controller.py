from fastapi import HTTPException, status
from database import chats, users
from services.openai import OpenAIService
from models.chat import ChatModel, ChatResponse, CreateChatRequest, DeleteChatResponse, DeleteAllChatsResponse
from bson import ObjectId
from datetime import datetime, timezone
from locales import get_message
from schemas.enums import Language

class ChatController:
    def __init__(self):
        self.openai_service = OpenAIService()
    
    async def get_chat_suggestions(self, user_id: str, user_language: str = "en"):
        """Get chat suggestion options"""
        try:
            # Convert string user_id to ObjectId
            try:
                object_id = ObjectId(user_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(user_language, "general.invalid_user_id")
                )
            
            # Verify user exists
            user = await users.find_one({"_id": object_id, "isDeleted": False})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(user_language, "auth.login.user_not_found")
                )
            
            # Return predefined chat suggestions
            suggestions = [
                {"title": "Help with coding", "value": "coding_help"},
                {"title": "Mental health support", "value": "mental_health"},
                {"title": "General conversation", "value": "general_chat"},
                {"title": "Learning assistance", "value": "learning_help"},
                {"title": "Problem solving", "value": "problem_solving"}
            ]
            
            return {
                "success": True,
                "message": get_message(user_language, "chat.suggestions.success"),
                "data": suggestions
            }
            
        except HTTPException:
            raise
        except Exception as error:
            print(f"ERROR getting chat suggestions: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_message(user_language, "general.internal_error")
            )
    
    async def get_saved_chats(self, user_id: str, user_language: str = "en"):
        """Get user's saved chat conversations"""
        try:
            # Convert string user_id to ObjectId
            try:
                object_id = ObjectId(user_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(user_language, "general.invalid_user_id")
                )
            
            # Verify user exists
            user = await users.find_one({"_id": object_id, "isDeleted": False})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(user_language, "auth.login.user_not_found")
                )
            
            # Get user's chats (excluding deleted ones)
            user_chats = await chats.find({
                "userId": str(object_id),
                "isDeleted": False
            }).sort("lastMessageAt", -1).to_list(length=100)
            
            # Format response
            saved_chats = []
            for chat in user_chats:
                saved_chats.append({
                    "chat_id": str(chat["_id"]),
                    "title": chat["title"],
                    "short_description": chat["short_description"]
                })
            
            return {
                "success": True,
                "message": get_message(user_language, "chat.saved.success"),
                "data": saved_chats
            }
            
        except HTTPException:
            raise
        except Exception as error:
            print(f"ERROR getting saved chats: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_message(user_language, "general.internal_error")
            )
    
    async def  create_chat(self, user_id: str, request: CreateChatRequest, user_language: str = "en"):
        """Create a new chat for the user"""
        try:
            # Convert string user_id to ObjectId
            try:
                object_id = ObjectId(user_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(user_language, "general.invalid_user_id")
                )
            
            # Verify user exists and is active
            user = await users.find_one({"_id": object_id, "isDeleted": False})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(user_language, "auth.login.user_not_found")
                )
            
            # Create new chat
            new_chat = {
                "userId": str(object_id),
                "title": request.title.strip(),
                "short_description": request.short_description.strip(),
                "is_temporary": request.is_temporary,
                "status": "active",
                "createdAt": datetime.now(timezone.utc),
                "updatedAt": datetime.now(timezone.utc),
                "lastMessageAt": datetime.now(timezone.utc),
                "messageCount": 0,
                "isDeleted": False
            }
            
            result = await chats.insert_one(new_chat)
            chat_id = str(result.inserted_id)
            
            # Return response
            return {
                "success": True,
                "message": get_message(user_language, "chat.create.success"),
                "data": {
                    "chatId": chat_id,
                    "title": new_chat["title"],
                    "short_description": new_chat["short_description"],
                    "is_temporary": new_chat["is_temporary"],
                    "status": new_chat["status"],
                    "createdAt": new_chat["createdAt"],
                    "updatedAt": new_chat["updatedAt"],
                    "lastMessageAt": new_chat["lastMessageAt"],
                    "messageCount": new_chat["messageCount"],
                    "isDeleted": new_chat["isDeleted"]
                }
            }
            
        except HTTPException:
            raise
        except Exception as error:
            print(f"ERROR creating chat: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_message(user_language, "general.internal_error")
            )
    
    async def delete_chat(self, user_id: str, chat_id: str, user_language: str = "en"):
        """Delete a specific chat (soft delete)"""
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
            
            # Find and verify chat belongs to user
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
            
            # Soft delete the chat
            now = datetime.now(timezone.utc)
            result = await chats.update_one(
                {"_id": chat_object_id},
                {
                    "$set": {
                        "isDeleted": True,
                        "status": "deleted",
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
                "message": get_message(user_language, "chat.delete.success"),
                "data": {
                    "chatId": chat_id,
                    "deletedAt": now
                }
            }
            
        except HTTPException:
            raise
        except Exception as error:
            print(f"ERROR deleting chat: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_message(user_language, "general.internal_error")
            )
    
    async def delete_all_chats(self, user_id: str, user_language: str = "en"):
        """Delete all chats for a user (soft delete)"""
        try:
            # Convert string user_id to ObjectId
            try:
                user_object_id = ObjectId(user_id)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(user_language, "general.invalid_user_id")
                )
            
            # Verify user exists
            user = await users.find_one({"_id": user_object_id, "isDeleted": False})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=get_message(user_language, "auth.login.user_not_found")
                )
            
            # Soft delete all user's chats
            now = datetime.now(timezone.utc)
            result = await chats.update_many(
                {
                    "userId": str(user_object_id),
                    "isDeleted": False
                },
                {
                    "$set": {
                        "isDeleted": True,
                        "status": "deleted",
                        "updatedAt": now
                    }
                }
            )
            
            return {
                "success": True,
                "message": get_message(user_language, "chat.delete_all.success"),
                "data": {
                    "deletedCount": result.modified_count,
                    "deletedAt": now
                }
            }
            
        except HTTPException:
            raise
        except Exception as error:
            print(f"ERROR deleting all chats: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=get_message(user_language, "general.internal_error")
            )
