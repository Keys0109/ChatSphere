from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
from enum import Enum

class ChatType(str, Enum):
    DIRECT = "direct"
    GROUP = "group"

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema as cs

        return cs.union_schema([
            cs.is_instance_schema(ObjectId),
            cs.chain_schema([
                cs.str_schema(),
                cs.no_info_plain_validator_function(cls.validate),
            ]),
        ], serialization=cs.to_string_ser_schema())

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return v
            raise ValueError("Invalid ObjectId")
        raise ValueError("Invalid ObjectId")

class ChatBase(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Name of the chat"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Description of the chat"
    )
    chat_type: ChatType = Field(
        default=ChatType.DIRECT,
        description="Type of the chat"
    )
    avatar: Optional[str] = Field(
        None,
        description="Avatar of the chat"
    )
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Chat 1",
                "description": "Description of the chat",
                "chat_type": "direct",
                "avatar": "https://example.com/avatar.jpg"
            }
        }
    )

class ChatCreate(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100
    )
    description: Optional[str] = Field(
        None,
        max_length=1000
    )
    chat_type: ChatType = Field(
        default=ChatType.DIRECT
    )
    avatar: Optional[str] = Field(
        None
    )
    participant_ids: List[str] = Field(
        ...,
        min_length=1,
        description="List of participant IDs"
    )

    @field_validator("participant_ids")
    @classmethod
    def validate_participant_ids(cls, v):
        for user_id in v:
            if not ObjectId.is_valid(user_id):
                raise ValueError(f"Invalid user ID: {user_id}")
        return v

    @field_validator("name", mode='before')
    @classmethod
    def validate_name(cls, v, info):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    model_config = ConfigDict(
        json_schema_extra={
            "example" : {
                "name": "Chat 1",
                "chat_type": "direct",
                "participant_ids": ["user1", "user2"]
            }
        }
    )
    

class ChatUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100
    )
    description: Optional[str] = Field(
        None,
        max_length=1000
    )
    avatar: Optional[str] = Field(
        None
    )
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated name",
                "description": "Updated Description of the chat",
            }
        }
    )

class AddParticipantRequest(BaseModel):
    user_id: str = Field(
        ...,
        description="User ID to add to the chat"
    )

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid user ID: {v}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "User ID to add to the chat"
            }
        }
    )

class RemoveParticipantRequest(BaseModel):
    user_id: str = Field(
        ...,
        description="User ID to remove from the chat"
    )

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid user ID: {v}")
        return v

class Chat(ChatBase):
    id: PyObjectId = Field(
        default_factory=PyObjectId,
        alias="_id"
    )
    participants: List[PyObjectId] = Field(
        ...,
        description="List of participant IDs"
    )
    admin: List[PyObjectId] = Field(
        ...,
        description="List of admin IDs"
    )
    created_by: PyObjectId = Field(
        ...,
        description="User ID of the creator"
    )
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_message_at: Optional[datetime] = Field(
        None,
        description="Timestamp of the last message"
    )
    last_message_preview: Optional[str] = Field(
        None,
        max_length=100,
        description="Preview of the last message"
    )
    is_archived: bool = Field(
        default=False,
        description="Whether the chat is archived"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str
        },
        json_schema_extra={
            "example": {
                "name": "Chat 1",
                "chat_type": "direct",
                "participants": ["user1", "user2"],
                "admin": ["user1"],
                "created_by": "user1",
                "created_at": "2022-01-01T00:00:00Z",
            }
        }
    )

class ChatResponse(ChatBase):
    id: str = Field(alias="_id")
    name: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    chat_type: ChatType
    avatar: Optional[str] = Field(None)
    participants: List[str] = []
    admin: List[str] = []
    created_by: str
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None
    last_message_preview: Optional[str] = None
    is_archived: bool = False


    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        json_encoders={
            ObjectId: str
        },
        json_schema_extra={
            "example": {
                "name": "Chat 1",
                "chat_type": "direct",
                "participants": ["user1", "user2"],
                "admin": ["user1"],
                "created_by": "user1",
                "created_at": "2022-01-01T00:00:00Z",
            }
        }
    )

class ChatSummary(BaseModel):
    id: str = Field(alias="_id")
    name: Optional[str] = None
    chat_type: ChatType = Field(default=ChatType.DIRECT)
    avatar: Optional[str] = None
    last_message_at: Optional[datetime] = None
    last_message_preview: Optional[str] = None
    unread_count: int = Field(default=0, description="Number of unread messages")
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        serialize_by_alias=True,
    )