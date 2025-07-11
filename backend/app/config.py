"""
Configuration management for the Iris Data API
"""

from typing import Optional, List
from pydantic_settings import BaseSettings
from functools import lru_cache
from datetime import timedelta


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    app_name: str = "Iris Data API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # JWT Authentication
    jwt_secret_key: str = "your-secret-key-here-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Security
    api_key: Optional[str] = None
    api_key_header: str = "X-API-Key"
    require_api_key: bool = False
    bcrypt_rounds: int = 12
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    cors_allow_credentials: bool = True
    
    # Data Configuration
    data_path: str = "data/iris.csv"
    cache_data: bool = True
    auto_reload_data: bool = False
    
    # User Access Control
    default_user_access: str = "setosa"
    available_species: List[str] = ["setosa", "versicolor", "virginica"]
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    workers: int = 1
    
    # Performance
    max_data_points: int = 10000
    enable_compression: bool = True
    request_timeout: int = 60
    
    # Documentation
    enable_docs: bool = True
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    
    # Database (for future use)
    database_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_prefix = "IRIS_API_"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()