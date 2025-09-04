from fastapi import APIRouter, Depends, HTTPException, status
from controllers.chat_controller import ChatController
from models.chat import CreateChatRequest, ChatResponse, DeleteChatResponse, DeleteAllChatsResponse
from middleware.auth import get_current_user
from locales import get_message
from schemas.enums import Language

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize chat controller
chat_controller = ChatController()

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
