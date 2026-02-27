import socketio
from typing import Dict, Optional
from loguru import logger

from .config import settings
from .utils.jwt import decode_token
from .services.user_service import set_user_online_status
from .services.chat_service import is_user_in_chat
from .services.message_service import create_message
from .services.redis_service import (
    set_user_online,
    set_user_offline,
    set_typing_status,
    get_typing_users,
)
from .models.message import MessageCreate, MessageResponse


# -----------------------------------------------------------------------------
# Socket.IO Server Setup
# -----------------------------------------------------------------------------

sio = socketio.AsyncServer(
    async_mode='asgi', 
    cors_allowed_origins=settings.cors_origins_list, 
    ping_timeout=settings.SOCKET_IO_PING_TIMEOUT, 
    ping_interval=settings.SOCKET_IO_PING_INTERVAL, 
    logger=False, 
    engineio_logger=False
)

socket_app = socketio.ASGIApp(
    sio, 
    socketio_path=settings.SOCKET_IO_PATH
)


# Connection State

connected_users: Dict[str, str] = {}
user_sessions: Dict[str, list] = {}


def get_user_id(sid: str) -> Optional[str]:
    return connected_users.get(sid)


def get_user_sids(user_id: str) -> list:
    return user_sessions.get(user_id, [])


# Socket Events

@sio.event
async def connect(sid: str, environ: dict, auth: dict = None):
    logger.info(f'Connection attempt from {sid}')

    token = None

    if auth and isinstance(auth, dict):
        token = auth.get('token')

    if not token:
        logger.warning(f'Connection rejected - no token: {sid}')
        return False
    
    try:
        payload = decode_token(token)
        user_id = payload.get('sub')

        if not user_id:
            logger.warning(f'Connection rejected - invalid token: {sid}')
            return False

        connected_users[sid] = user_id

        if user_id not in user_sessions:
            user_sessions[user_id] = []

        user_sessions[user_id].append(sid)

        await set_user_online(user_id)

        await set_user_online_status(user_id, True)

        await sio.enter_room(sid, f'user:{user_id}')

        logger.info(f'User {user_id} connected with session {sid}')
        await sio.emit('connected', {'user_id': user_id}, room=sid)
        return True

    except Exception as e:
        logger.error(f'Connection error: {e}')
        return False

@sio.event
async def disconnect(sid: str):
    user_id = connected_users.pop(sid, None)

    if user_id:
        if user_id in user_sessions:
            user_sessions[user_id].remove(sid)
            
            if not user_sessions[user_id]:
                del user_sessions[user_id]
                await set_user_offline(user_id)
                await set_user_online_status(user_id, False)
                logger.info(f'User {user_id} is now offline')

        logger.info(f'User {user_id} disconnected (session {sid})')
    else:
        logger.debug(f'Unknown session disconnected: {sid}')

@sio.event
async def join_chat(sid: str, data: dict):
    
    user_id = get_user_id(sid)
    
    if not user_id:
        await sio.emit('error', {'message': 'Not authenticated'}, room=sid)
        return
    
    chat_id = data.get('chat_id')
    
    if not chat_id:
        await sio.emit('error', {'message': 'chat_id required'}, room=sid)
        return
    
    if not await is_user_in_chat(chat_id, user_id):
        await sio.emit('error', {'message': 'Not a participant'}, room=sid)
        return
    
    room = f'chat:{chat_id}'
    
    await sio.enter_room(sid, room)
    
    logger.debug(f'User {user_id} joined chat room {chat_id}')
    
    await sio.emit('user_joined', {'user_id': user_id, 'chat_id': chat_id}, room=room, skip_sid=sid)

@sio.event
async def leave_chat(sid: str, data: dict):
    
    chat_id = data.get('chat_id')
    
    if chat_id: 
        
        room = f'chat:{chat_id}'
        
        await sio.leave_room(sid, room)
        
        logger.debug(f'Session {sid} left chat room {chat_id}')

@sio.event
async def send_message(sid: str, data: dict):
    
    user_id = get_user_id(sid)
    
    if not user_id:
        await sio.emit('error', {'message': 'Not authenticated'}, room=sid)
        return
    
    chat_id = data.get('chat_id')
    
    content = data.get('content')
    
    if not chat_id or not content:
        await sio.emit('error', {'message': 'chat_id and content required'}, room=sid)
        return
    
    if not await is_user_in_chat(chat_id, user_id):
        await sio.emit('error', {'message': 'Not a participant'}, room=sid)
        return
    
    try:
        message_data = MessageCreate(
            content=content,
            message_type=data.get('message_type', 'text'),
            reply_to=data.get('reply_to'),
            metadata=data.get('metadata'),
        )
        message = await create_message(chat_id, user_id, message_data)
        
        room = f'chat:{chat_id}'
        
        message_payload = MessageResponse(**message).model_dump(
            mode='json', by_alias=True
        )
        await sio.emit('new_message', message_payload, room=room)
        
        logger.debug(f'Message sent in chat {chat_id} by {user_id}')
    
    except Exception as e:
        logger.error(f'Error sending message: {e}')
        
        await sio.emit('error', {'message': 'Failed to send message'}, room=sid)

@sio.event
async def typing_start(sid: str, data: dict):
    
    user_id = get_user_id(sid)
    
    if not user_id:
        return
    
    chat_id = data.get('chat_id')
    
    if not chat_id:
        return
    
    await set_typing_status(chat_id, user_id, True)
    
    room = f'chat:{chat_id}'
    
    await sio.emit('user_typing', {'user_id': user_id, 'chat_id': chat_id, 'is_typing': True}, room=room, skip_sid=sid)

@sio.event
async def typing_stop(sid: str, data: dict):
    user_id = get_user_id(sid)
    if not user_id:
        return

    chat_id = data.get('chat_id')
    if not chat_id:
        return

    await set_typing_status(chat_id, user_id, False)
    room = f'chat:{chat_id}'
    await sio.emit(
        'user_typing',
        {'user_id': user_id, 'chat_id': chat_id, 'is_typing': False},
        room=room,
        skip_sid=sid,
    )

@sio.event
async def message_read(sid: str, data: dict):
    
    user_id = get_user_id(sid)
    
    if not user_id:
        return
    
    chat_id = data.get('chat_id')
    
    message_ids = data.get('message_ids', [])
    
    if not chat_id:
        return
    
    room = f'chat:{chat_id}'
    
    await sio.emit('messages_read', {'user_id': user_id, 'chat_id': chat_id, 'message_ids': message_ids}, room=room, skip_sid=sid)

async def emit_to_user(user_id: str, event: str, data: dict):
    
    room = f'user:{user_id}'
    
    await sio.emit(event, data, room=room)

async def emit_to_chat(chat_id: str, event: str, data: dict):
    
    room = f'chat:{chat_id}'
    
    await sio.emit(event, data, room=room)