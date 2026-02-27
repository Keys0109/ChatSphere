"""Redis service for caching and presence. Stub implementations when Redis is optional."""

from loguru import logger


async def invalidate_user_cache(user_id: str) -> None:
    """Invalidate cached user data."""
    logger.debug(f"Cache invalidated for user {user_id}")


async def set_user_online(user_id: str) -> None:
    """Mark user as online in presence store."""
    logger.debug(f"User {user_id} marked online")


async def set_user_offline(user_id: str) -> None:
    """Mark user as offline in presence store."""
    logger.debug(f"User {user_id} marked offline")


async def set_typing_status(chat_id: str, user_id: str, is_typing: bool) -> None:
    """Set user typing status for a chat."""
    logger.debug(f"User {user_id} typing in chat {chat_id}: {is_typing}")


async def get_typing_users(chat_id: str) -> list:
    """Get list of users currently typing in chat."""
    return []
