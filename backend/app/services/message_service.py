from typing import Optional, List, Dict
from datetime import datetime, timezone
from bson import ObjectId
from loguru import logger

from ..database import get_db
from ..models.message import Message, MessageCreate, MessageStatus


# Message CRUD Operations
async def create_message(
    chat_id: str,
    sender_id: str,
    message_data: MessageCreate
) -> Optional[dict]:
    db = get_db()

    message_doc = {
        "_id": ObjectId(),
        "chat_id": chat_id,
        "sender_id": sender_id,
        "content": message_data.content,
        "message_type": message_data.message_type.value if hasattr(message_data.message_type, 'value') else message_data.message_type,
        "reply_to": message_data.reply_to,
        "metadata": message_data.metadata if message_data.metadata is not None else {},
        "reactions": {},
        "status": MessageStatus.SENT,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "is_edited": False,
        "edited_at": None,
        "is_deleted": False,
        "deleted_at": None,
    }

    await db.messages.insert_one(message_doc)

    from .chat_service import update_last_message
    await update_last_message(chat_id, message_data.content, datetime.now(timezone.utc))
    
    
    logger.debug(f"Created message in chat {chat_id}")
    
    message_doc["_id"] = str(message_doc["_id"])
    return message_doc

async def get_message_by_id(message_id: str) -> Optional[dict]:
    db = get_db()
    
    message = await db.messages.find_one({"_id": ObjectId(message_id)})
    try:
        if message:
            message["_id"] = str(message["_id"])
        return message
    except Exception as e:
        logger.error(f"Error getting message by ID: {e}")
        return None

async def get_chat_messages(
    chat_id: str,
    limit: int = 50,
    before: Optional[datetime] =None,
    after: Optional[datetime] =None,
) -> List[dict]:

    db = get_db()

    filter_query = {"chat_id": chat_id, "is_deleted": {"$ne": True}}
    
    if before:
        filter_query["created_at"] = {"$lt": before}
    if after:
        filter_query["created_at"] = {"$gt": after}
    
    sort_order = -1 if before or not after else 1
    cursor = db.messages.find(filter_query).sort("created_at", sort_order).limit(limit)
    messages = await cursor.to_list(length=limit)
    
    for message in messages:
        message["_id"] = str(message["_id"])
        
    if after:
        messages.reverse()
        
    return messages

async def update_message_status(
    message_id: str,
    status: MessageStatus
) -> Optional[dict]:

    db = get_db()

    result = await db.messages.find_one_and_update(
        {"_id": ObjectId(message_id)},
        {"$set": {
            "status": status,
            "updated_at": datetime.now(timezone.utc)
        }},
        return_document=True
    )
    
    if result:
        result["_id"] = str(result["_id"])
    
    return result


async def mark_messages_as_read(
    chat_id: str,
    user_id: str,
    before_timestamp: Optional[datetime] = None
) -> int:
    db = get_db()
    
    filter_query = {
        "chat_id": chat_id,
        "sender_id": {"$ne": user_id},
        "status": {"$ne": MessageStatus.READ}
    }
    
    if before_timestamp:
        filter_query["created_at"] = {"$lte": before_timestamp}
    
    result = await db.messages.update_many(
        filter_query,
        {"$set": {"status": MessageStatus.READ}}
    )
    
    return result.modified_count


async def edit_message(message_id: str, new_content: str) -> Optional[dict]:
    db = get_db()
    
    result = await db.messages.find_one_and_update(
        {"_id": ObjectId(message_id)},
        {"$set": {
            "content": new_content,
            "is_edited": True,
            "edited_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }},
        return_document=True
    )
    
    if result:
        result["_id"] = str(result["_id"])
        logger.info(f"Edited message: {message_id}")
    
    return result


async def delete_message(message_id: str) -> Optional[dict]:
    """
    Soft delete a message.
    
    Args:
        message_id: Message's ID
        
    Returns:
        Updated message document or None if not found
    """
    db = get_db()
    
    result = await db.messages.find_one_and_update(
        {"_id": ObjectId(message_id)},
        {"$set": {
            "is_deleted": True,
            "deleted_at": datetime.now(timezone.utc),
            "content": "[Message deleted]",
            "updated_at": datetime.now(timezone.utc)
        }},
        return_document=True
    )
    
    if result:
        result["_id"] = str(result["_id"])
        logger.info(f"Deleted message: {message_id}")
    
    return result


# ==========================================
# Reaction Operations
# ==========================================

async def add_reaction(
    message_id: str,
    user_id: str,
    emoji: str
) -> Optional[dict]:
    
    db = get_db()
    
    # Add user to the list for this emoji
    result = await db.messages.find_one_and_update(
        {"_id": ObjectId(message_id)},
        {
            "$addToSet": {f"reactions.{emoji}": user_id},
            "$set": {"updated_at": datetime.now(timezone.utc)}
        },
        return_document=True
    )
    
    if result:
        result["_id"] = str(result["_id"])
    
    return result


async def remove_reaction(
    message_id: str,
    user_id: str,
    emoji: str
) -> Optional[dict]:
    db = get_db()
    
    # Remove user from the list for this emoji
    result = await db.messages.find_one_and_update(
        {"_id": ObjectId(message_id)},
        {
            "$pull": {f"reactions.{emoji}": user_id},
            "$set": {"updated_at": datetime.now(timezone.utc)}
        },
        return_document=True
    )
    
    if result:
        result["_id"] = str(result["_id"])
    
    return result


async def get_unread_count(chat_id: str, user_id: str) -> int:
    db = get_db()
    
    count = await db.messages.count_documents({
        "chat_id": chat_id,
        "sender_id": {"$ne": user_id},
        "status": {"$ne": MessageStatus.READ},
        "is_deleted": False
    })
    
    return count