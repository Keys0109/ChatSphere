from fastapi import APIRouter, HTTPException, Depends, status
from loguru import logger

from ..models.user import User, UserCreate, UserUpdate, UserResponse, UserLogin
from ..services.user_service import (
    create_user,
    get_user_by_id,
    get_user_by_email_for_auth,
    get_user_by_username_for_auth,
)
from ..utils.jwt import (
    create_jwt_token,
    create_refresh_token,
    decode_token,
    get_current_user_id,
)

from ..utils.security import verify_password, hash_password, validate_password_strength

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

# request and response models
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT Access Token")
    refresh_token: str = Field(..., description="JWT Refresh Token")
    token_type: str = Field(default="bearer", description="Token Type")
    user: Optional[UserResponse] = Field(None, description="User profile")

class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="JWT Refresh Token")

class MessageResponse(BaseModel):
    message: str = Field(..., description="Message")


# EndPoints

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user with email and password",
)
async def register_user(user_data: UserCreate) -> TokenResponse:
    valid, errors = validate_password_strength(user_data.password)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password is too weak", "errors": errors}
        )

    try:
        user = await create_user(user_data)
        token_data = {"sub": str(user["_id"]), "email": user["email"]}
        access_token = create_jwt_token(token_data)
        refresh_token = create_refresh_token(token_data)
        user_resp = UserResponse(**{**user, "_id": str(user["_id"])})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=user_resp,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Login user with email and password",
)
async def login_user(user_data: UserLogin) -> TokenResponse:
    user = None
    if user_data.email:
        user = await get_user_by_email_for_auth(user_data.email)
    elif user_data.username:
        user = await get_user_by_username_for_auth(user_data.username)

    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active",
        )
    
    token_data = {
        "sub": str(user["_id"]),
        "email": user["email"],
    }
    
    access_token = create_jwt_token(token_data)
    refresh_token = create_refresh_token(token_data)
    user.pop("password_hash", None)
    user_resp = UserResponse(**{**user, "_id": str(user["_id"])})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_resp,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the authenticated user's profile.",
)
async def get_me(user_id: str = Depends(get_current_user_id)):
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(**{**user, "_id": str(user["_id"])})


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh token",
    description="Refresh token with refresh token",
)
async def refresh_token(request: RefreshRequest) -> TokenResponse:
    try:
        payload = decode_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        
        user_id = payload.get("sub")

        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        
        access_token = create_jwt_token({"sub": user_id})
        refresh_token = create_refresh_token({"sub": user_id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )