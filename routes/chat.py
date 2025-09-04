from fastapi import APIRouter, Depends, HTTPException, status, Query
from controllers.chat_controller import ChatController
from controllers.message_controller import MessageController
from models.chat import CreateChatRequest, ChatResponse, DeleteChatResponse, DeleteAllChatsResponse
from models.message import (
    SendMessageRequest, UpdateMessageRequest, 
    ConversationResponse, SendMessageResponse, 
    UpdateMessageResponse, DeleteMessageResponse
)
from middleware.auth import get_current_user
from locales import get_message
from schemas.enums import Language

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize controllers
chat_controller = ChatController()
message_controller = MessageController()

@router.get("/suggestions", response_model=dict)
async def get_chat_suggestions(
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve available chat suggestion options
    """
    user_id = current_user["_id"]
    user_language = current_user.get("language", "english")
    
    # Convert database language to locale code for get_message
    if user_language == "french":
        locale_code = "fr"
    else:
        locale_code = "en"
    
    return await chat_controller.get_chat_suggestions(user_id, locale_code)

@router.get("/saved", response_model=dict)
async def get_saved_chats(
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve user's saved chat conversations
    """
    user_id = current_user["_id"]
    user_language = current_user.get("language", "english")
    
    # Convert database language to locale code for get_message
    if user_language == "french":
        locale_code = "fr"
    else:
        locale_code = "en"
    
    return await chat_controller.get_saved_chats(user_id, locale_code)

@router.post("/create", response_model=dict)
async def create_chat(
    request: CreateChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new chat conversation
    """
    user_id = current_user["_id"]
    user_language = current_user.get("language", "english")
    
    # Convert database language to locale code for get_message
    if user_language == "french":
        locale_code = "fr"
    else:
        locale_code = "en"
    
    return await chat_controller.create_chat(user_id, request, locale_code)

@router.delete("/all", response_model=dict)
async def delete_all_chats(
    current_user: dict = Depends(get_current_user)
):
    """
    Delete all chats for the authenticated user
    This is a soft delete - all chats are marked as deleted but not removed from database
    """
    user_id = current_user["_id"]
    user_language = current_user.get("language", "english")
    
    # Convert database language to locale code for get_message
    if user_language == "french":
        locale_code = "fr"
    else:
        locale_code = "en"
    
    return await chat_controller.delete_all_chats(user_id, locale_code)

@router.delete("/{chat_id}", response_model=dict)
async def delete_chat(
    chat_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a specific chat for the authenticated user
    This is a soft delete - the chat is marked as deleted but not removed from database
    """
    user_id = current_user["_id"]
    user_language = current_user.get("language", "english")
    
    # Convert database language to locale code for get_message
    if user_language == "french":
        locale_code = "fr"
    else:
        locale_code = "en"
    
    return await chat_controller.delete_chat(user_id, chat_id, locale_code)

@router.get("/{chat_id}/messages", response_model=dict)
async def get_conversation_messages(
    chat_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of messages per page"),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve paginated messages from a chat conversation
    """
    user_id = current_user["_id"]
    user_language = current_user.get("language", "english")
    
    # Convert database language to locale code for get_message
    if user_language == "french":
        locale_code = "fr"
    else:
        locale_code = "en"
    
    return await message_controller.get_conversation_messages(user_id, chat_id, page, limit, locale_code)

@router.post("/{chat_id}/message", response_model=dict)
async def send_message(
    chat_id: str,
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a message to the chatbot in a specific chat
    """
    user_id = current_user["_id"]
    user_language = current_user.get("language", "english")
    
    # Convert database language to locale code for get_message
    if user_language == "french":
        locale_code = "fr"
    else:
        locale_code = "en"
    
    return await message_controller.send_message(user_id, chat_id, request, locale_code)
