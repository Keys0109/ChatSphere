from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator, model_validator
from typing import Optional, List
from enum import Enum
from datetime import datetime, timezone
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema as cs 

        return cs.union_schema([
            cs.is_instance_schema(ObjectId),
            cs.chain_schema([
                cs.str_schema(),
                cs.no_info_plain_validator_function(PyObjectId.validate),
            ]),
        ], serialization = cs.to_string_ser_schema())

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return v
            raise ValueError("Invalid ObjectId")
        raise ValueError("Invalid ObjectId")

class UserBase(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username of the user"
    )
    email: EmailStr = Field(
        ...,
        description="Email of the user"
    )
    full_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Full name of the user"
    )
    avatar: Optional[str] = Field(
        None,
        description="Avatar of the user"
    )
    bio: Optional[str] = Field(
        None,
        max_length=1000,
        description="Bio of the user"
    )
    
    @field_validator("username", mode='before')
    @classmethod
    def validate_username(cls, v):
        if not v.strip():
            raise ValueError("Username cannot be empty")
        if not v.replace("_", "").isalnum():
            raise ValueError("Username can only contain letters, numbers and underscores")
        return v.strip().lower()
    

    
    model_config = ConfigDict(
        json_schema_extra= {
            "example": {
                "username": "user1",
                "email": "[EMAIL_ADDRESS]",
                "full_name": "User 1",
                "avatar": "https://example.com/avatar.jpg",
                "bio": "Bio of the user"
            }
        }
    )

class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password of the user"
    )

    model_config = ConfigDict(
        json_schema_extra= {
            "example": {
                "username": "user1",
                "email": "[EMAIL_ADDRESS]",
                "full_name": "User 1",
                "avatar": "https://example.com/avatar.jpg",
                "bio": "Bio of the user",
                "password": "password"
            }
        }
    )

class UserLogin(BaseModel):
    email: Optional[EmailStr] = Field(
        None,
        description="Email of the user"
    )
    username: Optional[str] = Field(
        None,
        description="Username of the user"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password of the user"
    )

    @model_validator(mode="after")
    def require_email_or_username(self):
        if not self.email and not self.username:
            raise ValueError("Either email or username is required")
        return self

    model_config = ConfigDict(
        json_schema_extra= {
            "example": {
                "email": "[EMAIL_ADDRESS]",
                "password": "password"
            }
        }
    )

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    avatar: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "John",
                "bio": "Updated bio text"
            }
        }
    )


class PasswordChange(BaseModel):
    """Password change request model."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class User(UserBase):
    id: PyObjectId = Field(
        default_factory=lambda: str(ObjectId()),
        alias="_id",
        description="MongoDB document ID"
    )
    password_hash: str = Field(
        ...,
        description="Hashed password (never expose to client)"
    )
    is_active: bool = Field(
        default=True,
        description="Whether the user account is active"
    )
    is_online: bool = Field(
        default=False,
        description="Whether the user is currently online"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Account creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp"
    )
    last_seen: Optional[datetime] = Field(
        None,
        description="Last activity timestamp"
    )
    
    model_config = ConfigDict(
        populate_by_name=True, 
        json_encoders={ObjectId: str}, 
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "username": "john_doe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password_hash": "$2b$12$...",
                "is_active": True,
                "is_online": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    )



class UserResponse(BaseModel):
    id: str = Field(alias="_id", description="User ID")
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    is_online: bool = False
    created_at: datetime
    last_seen: Optional[datetime] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        serialize_by_alias=True,
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "username": "john_doe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "is_online": True,
                "created_at": "2024-01-01T00:00:00Z",
                "last_seen": "2024-01-01T12:00:00Z"
            }
        }
    )


class UserSummary(BaseModel):
    id: str = Field(alias="_id")
    username: str
    avatar: Optional[str] = None
    is_online: bool = False

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        serialize_by_alias=True,
    )
