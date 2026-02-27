import re
from typing import Tuple, List, Dict, Any
import bcrypt
from loguru import logger
from fastapi import HTTPException, status
from ..config import settings

BCRYPT_ROUNDS = getattr(settings, "BCRYPT_ROUNDS", 12)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    try:
        salt = bcrypt.gensalt(BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error hashing password",
        )


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"), 
            hashed_password.encode("utf-8")
        )
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False

def validate_password_strength(password: str) -> tuple[bool, List[str]]:
    errors: List[str] = []
    
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        errors.append(
            f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters"
        )
    
    if settings.PASSWORD_REQUIRE_UPPERCASE:
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
    
    if settings.PASSWORD_REQUIRE_DIGITS:
        if not re.search(r"\d", password):
            errors.append("Password must contain at least one digit")
    
    if settings.PASSWORD_REQUIRE_SPECIAL:
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Password must contain at least one special character")
    
    is_valid = len(errors) == 0
    return is_valid, errors

def get_password_requirements() -> Dict[str, Any]:
    return {
        "min_length": settings.PASSWORD_MIN_LENGTH,
        "require_uppercase": settings.PASSWORD_REQUIRE_UPPERCASE,
        "require_digits": settings.PASSWORD_REQUIRE_DIGITS,
        "require_special": settings.PASSWORD_REQUIRE_SPECIAL,
    }