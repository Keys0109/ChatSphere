
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime
from loguru import logger

from ..models.message import (
    MessageCreate,
    MessageUpdate,
    MessageResponse,
    MessageStatus,
    ReactionRequest,
)
from ..services.message_service import (
    create_message,
    get_message_by_id,
    get_chat_messages,
    edit_message,
    delete_message,
    add_reaction,
    remove_reaction,
    mark_messages_as_read,
)
from ..services.chat_service import is_user_in_chat
from ..utils.jwt import get_current_user_id
from ..sio import emit_to_chat


router = APIRouter(prefix="/messages", tags=["Messages"])


# Response Models
from pydantic import BaseModel, Field


class MessageListResponse(BaseModel):
    """Response model for message list."""
    messages: List[MessageResponse] = Field(default_factory=list)
    count: int = Field(default=0)
    has_more: bool = Field(default=False)


@router.get(
    "/{chat_id}",
    response_model=MessageListResponse,
    summary="Get chat messages",
    description="Get messages from a chat with pagination."
)
async def get_messages(
    chat_id: str,
    limit: int = Query(50, ge=1, le=100, description="Number of messages"),
    before: Optional[datetime] = Query(None, description="Get messages before this time"),
    after: Optional[datetime] = Query(None, description="Get messages after this time"),
    user_id: str = Depends(get_current_user_id)
):
    if not await is_user_in_chat(chat_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant in this chat"
        )
    
    messages = await get_chat_messages(
        chat_id=chat_id,
        limit=limit + 1,  # Get one extra to check if there are more
        before=before,
        after=after
    )
    
    has_more = len(messages) > limit
    if has_more:
        messages = messages[:limit]
    
    message_responses = [MessageResponse(**m) for m in messages]
    
    return MessageListResponse(
        messages=message_responses,
        count=len(message_responses),
        has_more=has_more
    )


@router.post(
    "/{chat_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message",
    description="Send a new message to a chat."
)
async def send_message(
    chat_id: str,
    message_data: MessageCreate,
    user_id: str = Depends(get_current_user_id)
):
    if not await is_user_in_chat(chat_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant in this chat"
        )
    
    message = await create_message(chat_id, user_id, message_data)
    
    message_response = MessageResponse(**message)
    
    # Broadcast via WebSocket
    await emit_to_chat(chat_id, "new_message", message_response.model_dump(mode="json", by_alias=True))
    
    logger.debug(f"Message sent to chat {chat_id} by {user_id}")
    
    return message_response


@router.put(
    "/{message_id}",
    response_model=MessageResponse,
    summary="Edit a message",
    description="Edit the content of a message."
)
async def update_message(
    message_id: str,
    update_data: MessageUpdate,
    user_id: str = Depends(get_current_user_id)
):
    # Get the message
    message = await get_message_by_id(message_id)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if user is the sender
    if message["sender_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only edit your own messages"
        )

    updated_message = await edit_message(message_id, update_data.content)
    
    updated_response = MessageResponse(**updated_message)
    
    # Broadcast update via WebSocket
    await emit_to_chat(
        message["chat_id"],
        "message_updated",
        updated_response.model_dump(mode="json", by_alias=True)
    )
    
    logger.debug(f"Message {message_id} edited by {user_id}")
    
    return updated_response


@router.delete(
    "/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a message",
    description="Delete a message (soft delete)."
)
async def remove_message(
    message_id: str,
    user_id: str = Depends(get_current_user_id)
):
    # Get the message
    message = await get_message_by_id(message_id)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if user is the sender
    if message["sender_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only delete your own messages"
        )
    
    # Delete message
    await delete_message(message_id)
    

    await emit_to_chat(
        message["chat_id"],
        "message_deleted",
        {"message_id": message_id}
    )
    
    logger.debug(f"Message {message_id} deleted by {user_id}")


@router.post(
    "/{message_id}/reactions",
    response_model=MessageResponse,
    summary="Add reaction",
    description="Add a reaction to a message."
)
async def add_message_reaction(
    message_id: str,
    reaction: ReactionRequest,
    user_id: str = Depends(get_current_user_id)
):
    message = await get_message_by_id(message_id)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    if not await is_user_in_chat(message["chat_id"], user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant in this chat"
        )
    
    updated_message = await add_reaction(message_id, user_id, reaction.emoji)
    
    # Broadcast via WebSocket
    await emit_to_chat(
        message["chat_id"],
        "reaction_added",
        {
            "message_id": message_id,
            "user_id": user_id,
            "emoji": reaction.emoji
        }
    )
    
    return MessageResponse(**updated_message)


@router.delete(
    "/{message_id}/reactions/{emoji}",
    response_model=MessageResponse,
    summary="Remove reaction",
    description="Remove a reaction from a message."
)
async def remove_message_reaction(
    message_id: str,
    emoji: str,
    user_id: str = Depends(get_current_user_id)
):
    # Get the message
    message = await get_message_by_id(message_id)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Remove reaction
    updated_message = await remove_reaction(message_id, user_id, emoji)
    
    # Broadcast via WebSocket
    await emit_to_chat(
        message["chat_id"],
        "reaction_removed",
        {
            "message_id": message_id,
            "user_id": user_id,
            "emoji": emoji
        }
    )
    
    return MessageResponse(**updated_message)


@router.post(
    "/{chat_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark messages as read",
    description="Mark all messages in a chat as read."
)
async def mark_as_read(
    chat_id: str,
    user_id: str = Depends(get_current_user_id)
):
    # Check if user is in chat
    if not await is_user_in_chat(chat_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant in this chat"
        )
    
    count = await mark_messages_as_read(chat_id, user_id)
    
    # Broadcast via WebSocket
    await emit_to_chat(
        chat_id,
        "messages_read",
        {
            "chat_id": chat_id,
            "user_id": user_id,
            "count": count
        }
    )
    
    logger.debug(f"Marked {count} messages as read in chat {chat_id}")
