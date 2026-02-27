import motor.motor_asyncio
import redis.asyncio as redis
from typing import Optional
from loguru import logger

from .config import settings

mongo_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
mongo_db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
redis_client: Optional[redis.Redis] = None

async def connect_to_database():
    """Connect to MongoDB and Redis"""
    global mongo_client, mongo_db, redis_client
    
    try:
        global mongo_client
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.mongo_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            retryWrites=True,
            maxPoolSize=settings.MONGO_POOL_SIZE,
            maxIdleTimeMS=settings.MONGO_MAX_IDLE_TIME_MS,
        )
        await mongo_client.admin.command("ping")
        mongo_db = mongo_client[settings.MONGODB_NAME]
        logger.info(f"Connected to MongoDB: {settings.MONGODB_NAME}")

        await create_indexes()
    
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

async def disconnect_mongodb() -> None:
    global mongo_client, mongo_db, redis_client
    
    try:
        if mongo_client:
            mongo_client.close()
            logger.info("Disconnected from MongoDB")
    except Exception as e:
        logger.error(f"Failed to disconnect from MongoDB: {e}")
        raise
        
async def create_indexes() -> None:
    """create Database Indexes for improved quaries"""
    if mongo_db is None:
        raise RuntimeError("database not connected")

    logger.info("Creating database indexes...")

    try:
        await mongo_db.users.create_index("email", unique=True, background=True)
        await mongo_db.users.create_index("username", unique=True, background=True)
        await mongo_db.users.create_index("created_at", background=True)
        await mongo_db.users.create_index("is_online", background=True)
        await mongo_db.chats.create_index("participants", background=True)
        await mongo_db.chats.create_index("updated_at", background=True)
        await mongo_db.messages.create_index("chat_id", background=True)
        await mongo_db.messages.create_index("sender_id", background=True)
        await mongo_db.messages.create_index("timestamp", background=True)
        logger.info("All indexes created successfully")
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        raise


async def redis_connect():
    global redis_client

    logger.info("Connecting to Redis...")

    try:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD or None,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
        )
        await redis_client.ping()
        logger.info("Connected to Redis")
    except Exception as e:
        logger.warning(f"Redis unavailable (continuing without Redis): {e}")
        redis_client = None

async def disconnect_redis() -> None:
    global redis_client
    try:
        if redis_client:
            await redis_client.close()
            logger.info("Disconnected from Redis")
    except Exception as e:
        logger.error(f"Failed to disconnect from Redis: {e}")
        raise

async def close_db() -> None:
    """Close all database connections"""
    await disconnect_mongodb()
    await disconnect_redis()


async def disconnect_db() -> None:
    """Alias for close_db - shut down all DB connections"""
    await close_db()


async def connect_db():
    """Connect to all databases"""
    await connect_to_database()
    await redis_connect()


def get_db():
    return mongo_db

def get_redis():
    return redis_client