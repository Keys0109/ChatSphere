from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
from loguru import logger

from ..database import get_db
from ..models.chat import Chat, ChatCreate, ChatUpdate, ChatType

async def create_chat(chat_data: ChatCreate, creator_id: str) -> dict:
    db = get_db()

    participant_ids = list(chat_data.participant_ids)
    if creator_id not in participant_ids:
        participant_ids.insert(0, creator_id)

    if chat_data.chat_type == ChatType.DIRECT:
        if len(participant_ids) != 2:
            raise ValueError("Direct chat must have exactly two participants (including you)")
        sorted_ids = sorted(participant_ids)
        existing = await db.chats.find_one({
            "chat_type": ChatType.DIRECT,
            "participants": {"$all": sorted_ids, "$size": 2},
        })
        if existing:
            existing["_id"] = str(existing["_id"])
            return existing
        participants = sorted_ids
        name = chat_data.name or None
    else:
        if not chat_data.name:
            raise ValueError("Group chat name is required")
        participants = participant_ids
        name = chat_data.name

    chat_doc = {
        "_id": ObjectId(),
        "name": name,
        "description": chat_data.description,
        "chat_type": chat_data.chat_type.value if hasattr(chat_data.chat_type, "value") else chat_data.chat_type,
        "avatar": chat_data.avatar,
        "participants": participants,
        "admin": [creator_id],
        "created_by": creator_id,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "last_message_at": None,
        "last_message_preview": None,
        "is_archived": False,
    }

    await db.chats.insert_one(chat_doc)
    logger.info(f"Created new {chat_data.chat_type} chat: {chat_doc['_id']}")

    chat_doc["_id"] = str(chat_doc["_id"])
    return chat_doc


async def get_chat_by_id(chat_id: str) -> Optional[dict]:
    db = get_db()
    
    try:
        chat = await db.chats.find_one({"_id": ObjectId(chat_id)})
        if chat:
            chat["_id"] = str(chat["_id"])
        return chat
    except Exception as e:
        logger.warning(f"Error fetching chat {chat_id}: {e}")
        return None


async def get_user_chats(
    user_id: str,
    include_archived: bool = False
) -> List[dict]:
    db = get_db()

    filter_query = {"participants": user_id}
    if not include_archived:
        filter_query["is_archived"] = False
    
    cursor = db.chats.find(filter_query).sort([
        ("last_message_at", -1),
        ("created_at", -1)
    ])
    
    chats = await cursor.to_list(length=100)
    
    for chat in chats:
        chat["_id"] = str(chat["_id"])
    
    return chats


async def update_chat(chat_id: str, update_data: ChatUpdate) -> Optional[dict]:
    db = get_db()
    
    update_doc = {}
    for field, value in update_data.model_dump(exclude_unset=True).items():
        if value is not None:
            update_doc[field] = value
    
    if not update_doc:
        return await get_chat_by_id(chat_id)
    
    update_doc["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.chats.find_one_and_update(
        {"_id": ObjectId(chat_id)},
        {"$set": update_doc},
        return_document=True
    )
    
    if result:
        result["_id"] = str(result["_id"])
        logger.info(f"Updated chat: {chat_id}")
    
    return result


async def add_participant(chat_id: str, user_id: str) -> Optional[dict]:

    db = get_db()
    
    result = await db.chats.find_one_and_update(
        {"_id": ObjectId(chat_id)},
        {
            "$addToSet": {"participants": user_id},
            "$set": {"updated_at": datetime.now(timezone.utc)}
        },
        return_document=True
    )
    
    if result:
        result["_id"] = str(result["_id"])
        logger.info(f"Added user {user_id} to chat {chat_id}")
    
    return result


async def remove_participant(chat_id: str, user_id: str) -> Optional[dict]:
    db = get_db()
    
    result = await db.chats.find_one_and_update(
        {"_id": ObjectId(chat_id)},
        {
            "$pull": {"participants": user_id, "admin": user_id},
            "$set": {"updated_at": datetime.now(timezone.utc)}
        },
        return_document=True
    )
    
    if result:
        result["_id"] = str(result["_id"])
        logger.info(f"Removed user {user_id} from chat {chat_id}")
    
    return result


async def archive_chat(chat_id: str) -> Optional[dict]:
    db = get_db()
    
    result = await db.chats.find_one_and_update(
        {"_id": ObjectId(chat_id)},
        {"$set": {
            "is_archived": True,
            "updated_at": datetime.now(timezone.utc)
        }},
        return_document=True
    )
    
    if result:
        result["_id"] = str(result["_id"])
        logger.info(f"Archived chat: {chat_id}")
    
    return result


async def update_last_message(
    chat_id: str,
    message_preview: str,
    timestamp: datetime
) -> None:
    db = get_db()
    
    await db.chats.update_one(
        {"_id": ObjectId(chat_id)},
        {"$set": {
            "last_message_at": timestamp,
            "last_message_preview": message_preview[:100],  # Truncate
            "updated_at": datetime.now(timezone.utc)
        }}
    )


async def is_user_in_chat(chat_id: str, user_id: str) -> bool:
    db = get_db()
    
    chat = await db.chats.find_one({
        "_id": ObjectId(chat_id),
        "participants": user_id
    })
    
    return chat is not None


async def is_user_admin(chat_id: str, user_id: str) -> bool:
    db = get_db()
    
    chat = await db.chats.find_one({
        "_id": ObjectId(chat_id)
    })
    return chat is not None