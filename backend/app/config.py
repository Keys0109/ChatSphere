from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # MongoDB Settings
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGODB_NAME: str = "chatsphere"
    MONGO_POOL_SIZE: int = 10
    MONGO_MAX_IDLE_TIME_MS: int = 45000

    # JWT Settings
    JWT_SECRET_KEY: str = "4da4c141bbdabaa2aa85170dd42ebc707104bf2742021195849dec455570c0cde71f1787aecc519b50fea6d3b442ee3be9a63f3984be3805f230c5db205934ff"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    JWT_EXPIRATION_MINUTES: int = 60  # Access token (default 1 hour)
    JWT_REFRESH_EXPIRATION_MINUTES: int = 10080  # Refresh token (default 7 days)
    JWT_TIME_DELTA: int = 3600

    # Socket.IO Settings
    SOCKET_IO_PORT: int = 3000
    SOCKET_IO_PATH: str = "/socket.io"
    SOCKET_IO_PING_TIMEOUT: int = 60
    SOCKET_IO_PING_INTERVAL: int = 25

    # CORS Settings
    CORS_ORIGIN: str = "http://localhost:5173"
    CORS_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"

    # API Settings (metadata)
    API_PREFIX: str = "/api/v1"
    API_TITLE: str = "ChatSphere API"
    API_DESCRIPTION: str = "Real-time chat application API"
    API_VERSION: str = "1.0.0"

    # Ollama Settings (for local LLM)
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    OLLAMA_TIMEOUT: int = 120

    # OpenAI Settings (for GPT-4 features)
    OPENAI_API_KEY: str = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_API_TIMEOUT: int = 30

    # Redis Settings (for caching & presence)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_CACHE_EXPIRY: int = 3600

    # Rate Limiting Settings
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # HTTP Settings
    REQUEST_TIMEOUT: int = 30
    MAX_REQUEST_SIZE: int = 10485760

    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "7 days"

    # Security Settings
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_SPECIAL: bool = True
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_DIGITS: bool = True

    # Session Settings
    SESSION_TIMEOUT_MINUTES: int = 30

    # File Upload Settings
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_EXTENSIONS: str = "jpg,jpeg,png,gif,pdf,txt"

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.ALLOWED_FILE_EXTENSIONS.split(",")]

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGIN.split(",") if o.strip()]

    @property
    def cors_allow_methods_list(self) -> List[str]:
        parts = [m.strip() for m in self.CORS_ALLOW_METHODS.split(",") if m.strip()]
        return parts if parts else ["*"]

    @property
    def cors_allow_headers_list(self) -> List[str]:
        parts = [h.strip() for h in self.CORS_ALLOW_HEADERS.split(",") if h.strip()]
        return parts if parts else ["*"]
    
    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def mongo_uri(self) -> str:
        return self.MONGO_URI
    
    @property
    def mongo_client_options(self) -> dict:
        return {
            "maxPoolSize": self.MONGO_POOL_SIZE,
            "maxIdleTimeMS": self.MONGO_MAX_IDLE_TIME_MS,
        }
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

settings = Settings()