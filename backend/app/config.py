from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # MongoDB Settings
    MONGO_URI: str = Field(alias="MONGO_URI")
    MONGODB_NAME: str = Field(alias="MONGODB_NAME")
    MONGO_POOL_SIZE: int = Field(alias="MONGO_POOL_SIZE")
    MONGO_MAX_IDLE_TIME_MS: int = Field(alias="MONGO_MAX_IDLE_TIME_MS")

    # JWT Settings
    JWT_SECRET_KEY: str = Field(alias="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(alias="JWT_ALGORITHM")
    JWT_EXPIRATION_HOURS: int = Field(alias="JWT_EXPIRATION_HOURS")
    JWT_REFRESH_EXPIRATION_MINUTES: int = Field(alias="JWT_REFRESH_EXPIRATION_MINUTES")
    JWT_TIME_DELTA: int = Field(alias="JWT_TIME_DELTA")

    # Socket.IO Settings
    SOCKET_IO_PORT: int = Field(alias="SOCKET_IO_PORT")
    SOCKET_IO_PATH: str = Field(alias="SOCKET_IO_PATH")
    SOCKET_IO_PING_TIMEOUT: int = Field(alias="SOCKET_IO_PING_TIMEOUT")
    SOCKET_IO_PING_INTERVAL: int = Field(alias="SOCKET_IO_PING_INTERVAL")

    # CORS Settings
    CORS_ORIGIN: str = Field(alias="CORS_ORIGIN")
    CORS_CREDENTIALS: Optional[bool] = Field(alias="CORS_CREDENTIALS")
    CORS_ALLOW_METHODS: str = Field(alias="CORS_ALLOW_METHODS")
    CORS_ALLOW_HEADERS: str = Field(alias="CORS_ALLOW_HEADERS")

    # API Settings (metadata)
    API_PREFIX: str = "/api/v1"
    API_TITLE: str = "ChatSphere API"
    API_DESCRIPTION: str = "Real-time chat application API"
    API_VERSION: str = "1.0.0"

    # Redis Settings (for caching & presence)
    REDIS_HOST: str = Field(alias="REDIS_HOST")
    REDIS_PORT: int = Field(alias="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(alias="REDIS_PASSWORD")
    REDIS_DB: int = Field(alias="REDIS_DB")
    REDIS_CACHE_EXPIRY: int = 3600

    # Rate Limiting Settings
    RATE_LIMIT_ENABLED: bool = Field(alias="RATE_LIMIT_ENABLED")
    RATE_LIMIT_DEFAULT: str = Field(alias="RATE_LIMIT_DEFAULT")
    RATE_LIMIT_WINDOW: int = Field(alias="RATE_LIMIT_WINDOW")

    # HTTP Settings
    REQUEST_TIMEOUT: int = Field(alias="REQUEST_TIMEOUT")
    MAX_REQUEST_SIZE: int = Field(alias="MAX_REQUEST_SIZE")

    # Logging Settings
    LOG_LEVEL: str = Field(alias="LOG_LEVEL")
    LOG_FILE: str = Field(alias="LOG_FILE")
    LOG_ROTATION: str = Field(alias="LOG_ROTATION")
    LOG_RETENTION: str = Field(alias="LOG_RETENTION")

    # Security Settings
    PASSWORD_MIN_LENGTH: int = Field(alias="PASSWORD_MIN_LENGTH")
    PASSWORD_REQUIRE_SPECIAL: bool = Field(alias="PASSWORD_REQUIRE_SPECIAL")
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(alias="PASSWORD_REQUIRE_UPPERCASE")
    PASSWORD_REQUIRE_DIGITS: bool = Field(alias="PASSWORD_REQUIRE_DIGITS")

    # Session Settings
    SESSION_TIMEOUT_MINUTES: int = Field(alias="SESSION_TIMEOUT_MINUTES")

    # File Upload Settings
    MAX_FILE_SIZE_MB: int = Field(alias="MAX_FILE_SIZE_MB")
    ALLOWED_FILE_EXTENSIONS: str = Field(alias="ALLOWED_FILE_EXTENSIONS")

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
