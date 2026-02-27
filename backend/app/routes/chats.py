from fastapi import APIRouter, Depends, HTTPException, status, Query
from loguru import logger
from typing import List, Optional

from ..models.chat import (
    ChatCreate,
    ChatResponse,
    ChatUpdate,
    AddParticipantRequest,
    ChatSummary,
)
from ..services.chat_service import (
    create_chat,
    get_chat_by_id,
    get_user_chats,
    update_chat,
    add_participant,
    remove_participant,
    is_user_in_chat,
    is_user_admin,
    archive_chat,
)
from ..services.user_service import get_user_by_id
from ..utils.jwt import get_current_user_id


router = APIRouter(
    prefix="/chats",
    tags=["chats"],
)


# response models for chat routes
from pydantic import BaseModel, Field
from typing import List, Optional
from ..models.user import UserSummary

class ChatListResponse(BaseModel):
    chats: List[ChatSummary] = Field(default_factory=list)
    total: int = Field(default=0)

class ChatDetailResponse(BaseModel):
    participants: List[UserSummary] = Field(default_factory=list)




@router.get(
    "/",
    response_model=ChatListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all chats for the current user",
    description="Get all chats for the current user",
)
async def chat_list(    
    include_archived: bool = Query(False, description="Include archived chats"),
    user_id: str = Depends(get_current_user_id)
):

    chats = await get_user_chats(user_id, include_archived=include_archived)

    chat_summeries = [
        ChatSummary(
            _id=c["_id"],
            name=c.get("name"),
            chat_type=c["chat_type"],
            avatar=c.get("avatar"),
            last_message_at=c.get("last_message_at"),
            last_message_preview=c.get("last_message_preview"),
            unread_count=0  # TODO: Calculate from message service
        )
        for c in chats
    ]

    return ChatListResponse(
        chats=chat_summeries,
        total=len(chats)
    )



@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat",
    description="Create a new chat",
)
async def create_new_chat(
    chat_data:ChatCreate,
    user_id: str = Depends(get_current_user_id)
):
    try:
        chat = await create_chat(chat_data, user_id)
        logger.info(f"Chat created successfully: {chat['_id']}")
        return ChatResponse(**chat)
    except Exception as e:
        logger.error(f"Error creating chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/{chat_id}",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a chat by ID",
    description="Get a chat by ID",
)
async def get_chat(
    chat_id: str,
    user_id: str = Depends(get_current_user_id)
):
    try:
        chat = await get_chat_by_id(chat_id)
        if not chat:
            logger.info(f"Chat not found: {chat_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        if not await is_user_in_chat(chat_id, user_id):
            logger.info(f"User {user_id} is not a member of chat {chat_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of this chat"
            )
        return ChatResponse(**chat)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    '/{chat_id}', 
    response_model=ChatDetailResponse, 
    summary='Get chat details', 
    description='Get detailed information about a specific chat.'
)

async def get_chat_details(
    chat_id: str, 
    user_id: str=Depends(get_current_user_id)
):
    if not await is_user_in_chat(chat_id, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not a participant in this chat')

    chat = await get_chat_by_id(chat_id)


    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Chat not found'
        )

    participant_users = await get_users_by_ids(chat['participants'])

    participant_details = [UserSummary(
        _id=u['_id'], 
        username=u['username'], 
        avatar=u.get('avatar'), 
        is_online=u.get('is_online', False)
    ) for u in participant_users
    ]
    
    return ChatDetailResponse(
        **chat, 
        participants=participant_details
    )

@router.put(
    '/{chat_id}', 
    response_model=ChatResponse, 
    summary='Update chat', 
    description='Update chat name, description, or avatar.'
)
async def update_chat_details(
    chat_id: str, 
    update_data: ChatUpdate, 
    user_id: str=Depends(get_current_user_id)
):
    chat = await get_chat_by_id(chat_id)
    logger.info(f'Updating chat {chat_id} with data {update_data}')
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Chat not found')
    logger.info(f'Chat {chat_id} found for user {user_id}')


    if chat['chat_type'] == 'group':
        if not await is_user_admin(chat_id, user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only admins can update group chats')

    elif not await is_user_in_chat(chat_id, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not a participant in this chat')

    updated_chat = await update_chat(chat_id, update_data)

    logger.info(f'Chat {chat_id} updated by user {user_id}')

    return ChatResponse(**updated_chat)


@router.delete(
    '/{chat_id}', 
    status_code=status.HTTP_204_NO_CONTENT, 
    summary='Archive chat', 
    description='Archive a chat (soft delete).'
)
async def delete_chat(
    chat_id: str, 
    user_id: str=Depends(get_current_user_id)
):

    if not await is_user_in_chat(chat_id, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not a participant in this chat')

    await archive_chat(chat_id)
    logger.info(f'Chat {chat_id} archived by user {user_id}')


@router.post(
    '/{chat_id}/participants', 
    response_model=ChatResponse, 
    summary='Add participant', 
    description='Add a user to a group chat.'
)
async def add_chat_participant(chat_id: str, 
    request: AddParticipantRequest, 
    user_id: str=Depends(get_current_user_id)
):

    chat = await get_chat_by_id(chat_id)

    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Chat not found')

    if chat['chat_type'] != 'group':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot add participants to direct chats')

    if not await is_user_admin(chat_id, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only admins can add participants')

    updated_chat = await add_participant(chat_id, request.user_id)

    logger.info(f'User {request.user_id} added to chat {chat_id}')

    return ChatResponse(**updated_chat)

@router.delete(
    '/{chat_id}/participants/{target_user_id}', 
    response_model=ChatResponse, 
    summary='Remove participant', 
    description='Remove a user from a group chat.'
)
async def remove_chat_participant(
    chat_id: str, 
    target_user_id: str, 
    user_id: str=Depends(get_current_user_id)
):

    chat = await get_chat_by_id(chat_id)

    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Chat not found')
    
    if chat['chat_type'] != 'group':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot remove participants from direct chats')
    
    if target_user_id != user_id:
        if not await is_user_admin(chat_id, user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only admins can remove other participants')
    
    updated_chat = await remove_participant(chat_id, target_user_id)

    logger.info(f'User {target_user_id} removed from chat {chat_id}')
    
    return ChatResponse(**updated_chat)