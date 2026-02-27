import sys
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger

from app.config import settings
from app.database import connect_db, disconnect_db
from app.sio import socket_app
from app.routes import auth_router, users_router, chats_router, messages_router

def setup_logging():
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format='<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>',
        level=settings.LOG_LEVEL,
    )
    logger.add(
        settings.LOG_FILE,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        format='{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}',
        level=settings.LOG_LEVEL,
    )
    logger.info(f'Logging configured at {settings.LOG_LEVEL} level')
setup_logging()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT] if settings.RATE_LIMIT_ENABLED else [],
    enabled=settings.RATE_LIMIT_ENABLED,
)


# Application Lifecycle

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Starting ChatSphere API...')
    await connect_db()
    logger.success('✓ Application started successfully')
    yield
    logger.info('Shutting down ChatSphere API...')
    await disconnect_db()
    logger.info('✓ Application shutdown complete')


# FastAPI App

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_url='/openapi.json',
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Exception Handlers

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = '.'.join((str(loc) for loc in error['loc'][1:]))
        message = error['msg']
        errors.append({'field': field, 'message': message})
    logger.warning(f'Validation error: {errors}')
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            'success': False,
            'message': 'Validation error',
            'errors': errors,
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f'Unexpected error: {exc}')
    if settings.DEBUG:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'success': False,
                'message': str(exc),
                'type': type(exc).__name__,
            },
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'success': False, 'message': 'Internal server error'},
    )


# -----------------------------------------------------------------------------
# Middleware & Routes
# -----------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.cors_allow_methods_list,
    allow_headers=settings.cors_allow_headers_list,
)
app.mount('/socket.io', socket_app)


@app.get(
    '/health',
    tags=['Health'],
    summary='Health check',
    description='Check if the API is running.',
)
async def health_check():
    return {
        'status': 'ok',
        'environment': settings.ENVIRONMENT,
        'version': settings.API_VERSION,
    }


app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(users_router, prefix=settings.API_PREFIX)
app.include_router(chats_router, prefix=settings.API_PREFIX)
app.include_router(messages_router, prefix=settings.API_PREFIX)

def main():
    logger.info(f'Starting server in {settings.ENVIRONMENT} mode...')
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == '__main__':
    main()