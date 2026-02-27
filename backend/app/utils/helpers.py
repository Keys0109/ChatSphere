from typing import Dict, Any, Optional, TypeVar, List
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId

T = TypeVar("T")


def serialize_object_id(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {key: serialize_object_id(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_object_id(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj


def parse_Object_id(id_str: str) -> Optional[ObjectId]:
    try:
        return ObjectId(id_str)
    except InvalidId:
        return None


def is_valid_object_id(id_str: str) -> bool:
    return parse_Object_id(id_str) is not None


def paginate_params(page: int = 1, limit: int = 20) -> Dict[str, int]:
    page = max(1, page)
    limit = min(max(1, limit), 100)

    skip - (page-1) * limit

    return {"skip": skip, "limit": limit}

def create_pagination_response(
    itmes: List[T],
    total: int,
    page: int,
    limit: int
) -> Dict[str, Any]:

    total_pages = (total + limit - 1) // limit
    return {

        "items": itmes,
        "pagimation": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": page * limit < total,
            "has_prev": page > 1,
        }
    }


def success_response(
    data: Any = None,
    message: str = "success"
) -> Dict[str, Any]:
    response = {
        "status": "success",
        "message": message,
    }
    if data is not None:
        response["data"] = data
    return response


def error_response(
    message: str,
    error: str = "error"
) -> Dict[str, Any]:
    
    response = {
        "message": message,
        "error": error,
    }

    
    if errors:
        response["errors"] = errors
    
    return response

def utc_now() -> datetime:
    return datetime.now(timezone.utc)