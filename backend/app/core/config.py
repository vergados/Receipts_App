"""Application configuration."""
from functools import lru_cache
from typing import Literal
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")
    app_name: str = "Receipts API"
    app_version: str = "1.0.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    database_url: str = Field(default="sqlite:///./receipts.db")
    db_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10
    secret_key: str = Field(default="CHANGE-THIS-IN-PRODUCTION")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    reset_token_expire_hours: int = 1
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://192.168.1.20:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    storage_backend: Literal["local", "s3"] = "local"
    storage_local_path: str = "./uploads"
    max_image_size_mb: int = 50
    max_video_size_mb: int = 100
    allowed_image_types: list[str] = ["image/png", "image/jpeg", "image/gif", "image/webp"]
    allowed_video_types: list[str] = ["video/mp4", "video/webm"]
    rate_limit_enabled: bool = True
    rate_limit_auth_per_minute: int = 60
    rate_limit_read_per_minute: int = 600
    rate_limit_write_per_minute: int = 120
    rate_limit_upload_per_minute: int = 10
    rate_limit_export_per_minute: int = 5
    export_card_width: int = 1200
    export_card_quality: int = 90
    storage_s3_bucket: str = ""
    storage_s3_region: str = "us-east-1"
    newsroom_enabled: bool = False
    newsroom_beta_users: list[str] = []
    @computed_field
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    @computed_field
    @property
    def max_image_size_bytes(self) -> int:
        return self.max_image_size_mb * 1024 * 1024

    @computed_field
    @property
    def max_video_size_bytes(self) -> int:
        return self.max_video_size_mb * 1024 * 1024

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
