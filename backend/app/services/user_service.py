from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId
from loguru import logger
from fastapi import HTTPException, status

from ..database import get_db
from ..models.user import User, UserCreate, UserUpdate, UserResponse
from ..utils.security import hash_password

# User CRUD Operations
async def create_user(user_data: UserCreate) -> dict:
    db = get_db()
    
    
    
    existing_email = await db.users.find_one({"email": user_data.email})
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )
    
    existing_username = await db.users.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    
    full_name = getattr(user_data, "full_name", None) or ""
    parts = full_name.strip().split(None, 1) if full_name else []
    first_name = parts[0] if parts else None
    last_name = parts[1] if len(parts) > 1 else None

    user_doc = {
        "_id": ObjectId(),
        "username": user_data.username.lower(),
        "email": user_data.email.lower(),
        "password_hash": hash_password(user_data.password),
        "first_name": first_name,
        "last_name": last_name,
        "avatar": user_data.avatar,
        "bio": user_data.bio,
        "is_active": True,
        "is_online": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "last_seen": None,
    }

    result = await db.users.insert_one(user_doc)
    del user_doc["password_hash"]

    return user_doc


async def get_user_by_id(user_id: str) -> Optional[dict]:
    db = get_db()
    if not ObjectId.is_valid(user_id):
        return None
    user = await db.users.find_one(
        {"_id": ObjectId(user_id)},
        {"password_hash": 0}
    )
    if user:
        user["_id"] = str(user["_id"])
    return user


async def get_user_by_email(email: str) -> Optional[dict]:
    db = get_db()

    user = await db.users.find_one({"email": email.lower()})
    if user:
        user["_id"] = str(user["_id"])
    return user


async def get_user_by_email_for_auth(email: str) -> Optional[dict]:
    """Returns user with password_hash for authentication."""
    db = get_db()
    user = await db.users.find_one({"email": email.lower()})
    if user:
        user["_id"] = str(user["_id"])
    return user


async def get_user_by_username_for_auth(username: str) -> Optional[dict]:
    """Returns user with password_hash for authentication."""
    db = get_db()
    user = await db.users.find_one({"username": username.lower()})
    if user:
        user["_id"] = str(user["_id"])
    return user


async def get_user_by_username(username: str) -> Optional[dict]:
    db = get_db()

    user = await db.users.find_one(
        {"username": username.lower()},
        {"password_hash": 0}
    )
    if user:
        user["_id"] = str(user["_id"])
    return user

async def update_user(user_id: str, update_data: UserUpdate) -> Optional[dict]:
    db = get_db()

    update_doc = {}
    for field, value in update_data.model_dump(exclude_unset=True).items():
        if value is not None:
            update_doc[field] = value
    
    if not update_doc:
        return await get_user_by_id(user_id)
    
    update_doc["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_doc},
        return_document=True 
    )
    
    if result:
        result["_id"] = str(result["_id"])
        logger.info(f"Updated user: {user_id}")
    
    return result


async def set_user_online_status(user_id: str, is_online: bool) -> bool:
    db = get_db()

    update_doc = {
        "is_online": is_online,
        "updated_at": datetime.now(timezone.utc),
    }

    if not is_online:
        update_doc["last_seen"] = datetime.now(timezone.utc)
    
    result = await db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_doc},
        return_document=True
    )
    
    logger.debug(f"User {user_id} set online status to {is_online}")
    return result is not None

async def search_user(
    query: str,
    limit: int = 20,
    exclude_ids: Optional[List[str]] = None
) -> List[dict]:
    db = get_db()

    search_filter = {
        "$and": [
            {"$or": [
                {"username": {"$regex": query, "$options": "i"}},
                {"email": {"$regex": query, "$options": "i"}},
            ]}
        ]
    }
    if exclude_ids:
        valid_ids = [ObjectId(id_str) for id_str in exclude_ids if ObjectId.is_valid(id_str)]
        if valid_ids:
            search_filter["$and"].append({"_id": {"$nin": valid_ids}})
    
    cursor = db.users.find(
        search_filter,
        {"password_hash": 0}
    ).limit(limit)

    users = await cursor.to_list(length=limit)

    for user in users:
        user["_id"] = str(user["_id"])
    
    return users


search_users = search_user  # alias

async def get_users_by_id(user_ids: List[str]) -> List[dict]:
    db = get_db()
    
    object_ids = [ObjectId(id) for id in user_ids if ObjectId.is_valid(id)]
    
    cursor = db.users.find(
        {"_id": {"$in": object_ids}},
        {"password_hash": 0} 
    )
    
    users = await cursor.to_list(length=len(object_ids))
    
    for user in users:
        user["_id"] = str(user["_id"])
    
    return users
