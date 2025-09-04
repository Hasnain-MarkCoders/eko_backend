from fastapi import APIRouter, Depends, HTTPException, status
from controllers.message_controller import MessageController
from models.message import (
    UpdateMessageRequest, 
    UpdateMessageResponse, DeleteMessageResponse
)
from middleware.auth import get_current_user
from locales import get_message
from schemas.enums import Language

router = APIRouter(prefix="/message", tags=["messages"])

# Initialize message controller
message_controller = MessageController()


@router.put("/{message_id}", response_model=dict)
async def update_message(
    message_id: str,
    request: UpdateMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a specific message
    """
    user_id = current_user["_id"]
    user_language = current_user.get("language", "english")
    
    # Convert database language to locale code for get_message
    if user_language == "french":
        locale_code = "fr"
    else:
        locale_code = "en"
    
    return await message_controller.update_message(user_id, message_id, request, locale_code)

@router.delete("/{message_id}", response_model=dict)
async def delete_message(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a specific message
    """
    user_id = current_user["_id"]
    user_language = current_user.get("language", "english")
    
    # Convert database language to locale code for get_message
    if user_language == "french":
        locale_code = "fr"
    else:
        locale_code = "en"
    
    return await message_controller.delete_message(user_id, message_id, locale_code)
