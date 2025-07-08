"""
Configuration management for the Iris Data API
"""

from typing import Optional, List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    app_name: str = "Iris Data API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api"
    
    # Security
    api_key: Optional[str] = None
    api_key_header: str = "X-API-Key"
    require_api_key: bool = False
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    cors_allow_credentials: bool = True
    
    # Data Configuration
    data_path: str = "data/iris.csv"
    cache_data: bool = True
    auto_reload_data: bool = False
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # Performance
    max_data_points: int = 10000
    enable_compression: bool = True
    
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