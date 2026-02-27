from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from loguru import logger

from ..models.user import UserUpdate, UserResponse, UserSummary
from ..services.user_service import get_user_by_id, update_user, search_users
from ..utils.jwt import get_current_user_id
from ..services.redis_service import invalidate_user_cache


router = APIRouter(prefix='/users', tags=['Users'])


# Models

class SearchResponse(BaseModel):
    users: List[UserSummary] = Field(default_factory=list)
    count: int = Field(default=0)


# Routes

@router.get(
    '/me', 
    response_model=UserResponse, 
    summary='Get current user profile', 
    description="Get the authenticated user's full profile."
)
async def get_my_profile(
    user_id: str=Depends(get_current_user_id)
):
    user = await get_user_by_id(user_id)
    logger.info(f'User profile retrieved: {user_id}')

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    return UserResponse(**user)


@router.put(
    '/me', 
    response_model=UserResponse, 
    summary='Update current user profile', 
    description="Update the authenticated user's profile fields."
)
async def update_my_profile(
    update_data: UserUpdate,
    user_id: str=Depends(get_current_user_id)
):
    updated_user = await update_user(user_id, update_data)

    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    await invalidate_user_cache(user_id)

    logger.info(f'User profile updated: {user_id}')

    return UserResponse(**updated_user)


@router.get(
    '/search', 
    response_model=SearchResponse, 
    summary='Search users', 
    description='Search for users by username or email.'
)
async def search_for_users(
    q: str=Query(..., min_length=2, description='Search query'), 
    limit: int=Query(20, ge=1, le=50, description='Max results'), 
    user_id: str=Depends(get_current_user_id)
):
    users = await search_users(
        query=q,
        limit=limit,
        exclude_ids=[user_id],
    )
    
    user_summaries = [
        UserSummary(
            _id=u['_id'], 
            username=u['username'], 
            avatar=u.get('avatar'), 
            is_online=u.get('is_online', False)
        ) 
        for u in users
    ]
    
    logger.info(f'Users searched: {user_id}')
    
    return SearchResponse(users=user_summaries, count=len(user_summaries))


@router.get(
    '/{user_id}', 
    response_model=UserResponse, 
    summary='Get user by ID', 
    description="Get a specific user's public profile."
)
async def get_user_profile(
    user_id: str, 
    current_user_id: str=Depends(get_current_user_id)
):
    user = await get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    return UserResponse(**user)