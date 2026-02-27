from pydantic import BaseModel, Field, ConfigDict, field_validator, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime, timezone
from bson import ObjectId

class MessageStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"
    SYSTEM = "system"
    AI = "ai"


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

class MessageBase(BaseModel):
    
    content: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Content of the message"
    )
    message_type: MessageType = Field(
        default=MessageType.TEXT,
        description="Type of the message"
    )

    model_config = ConfigDict(
        json_schema_extra= {
            "example": {
                "content": "Hello, how are you?",
                "message_type": "text",
            }
        }
    )

class MessageCreate(MessageBase):
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Message content"
    )
    message_type: MessageType = Field(
        default=MessageType.TEXT,
        description="Type of message"
    )
    reply_to: Optional[str] = Field(
        None,
        description="ID of message being replied to"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional data (file info, image dimensions, etc.)"
    )
    @field_validator("content")
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        if v is None and not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return v

class MessageUpdate(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Updated message content"
    )


class ReactionRequest(BaseModel):
    emoji: str = Field(
        ...,
        max_length=10,
        description="Emoji reaction (e.g., '👍', '❤️')"
    )
    
    @field_validator("emoji")
    @classmethod
    def validate_emoji(cls, v: str) -> str:
        """Basic emoji validation."""
        # Remove whitespace
        v = v.strip()
        if not v:
            raise ValueError("Emoji cannot be empty")
        return v



class Message(MessageBase):
    id: PyObjectId = Field(
        default_factory=lambda: str(ObjectId()),
        alias="_id",
        description="MongoDB document ID"
    )
    chat_id: str = Field(
        ...,
        description="ID of the chat this message belongs to"
    )
    sender_id: str = Field(
        ...,
        description="ID of the user who sent the message"
    )
    status: MessageStatus = Field(
        default=MessageStatus.SENT,
        description="Message delivery status"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Message creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp"
    )
    
    is_edited: bool = Field(
        default=False,
        description="Whether message has been edited"
    )
    edited_at: Optional[datetime] = Field(
        None,
        description="Timestamp of last edit"
    )
    
    reply_to: Optional[str] = Field(
        None,
        description="ID of message being replied to"
    )
    
    reactions: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Reactions mapped to user IDs"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional message metadata"
    )
    
    is_deleted: bool = Field(
        default=False,
        description="Whether message has been deleted"
    )
    deleted_at: Optional[datetime] = Field(
        None,
        description="Deletion timestamp"
    )
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "content": "Hello!",
                "chat_id": "507f1f77bcf86cd799439012",
                "sender_id": "507f1f77bcf86cd799439013",
                "message_type": "text",
                "status": "delivered",
                "created_at": "2024-01-01T00:00:00Z",
                "reactions": {"👍": ["user_id_1"]},
                "is_edited": False
            }
        }
    )


class MessageResponse(BaseModel):
    id: str = Field(alias="_id")
    content: str
    chat_id: str
    sender_id: str
    message_type: MessageType
    status: MessageStatus
    created_at: datetime
    updated_at: datetime
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    reply_to: Optional[str] = None
    reactions: Dict[str, List[str]] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_deleted: bool = False
    
    @field_validator("reactions", mode="before")
    @classmethod
    def validate_reactions(cls, v):
        return v if v is not None else {}
    
    @field_validator("metadata", mode="before")
    @classmethod
    def validate_metadata(cls, v):
        return v if v is not None else {}
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        serialize_by_alias=True,
    )


class MessageWithSender(MessageResponse):
    sender_username: Optional[str] = None
    sender_avatar: Optional[str] = None
