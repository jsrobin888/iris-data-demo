"""
Health check routes
"""

from fastapi import APIRouter
from datetime import datetime
import psutil
import platform

from ...models.schemas import HealthResponse
from ...config import settings
from ...data.loader import get_data_loader

router = APIRouter(tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check endpoint"""
    loader = get_data_loader()
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        data_loaded=loader.is_loaded
    )


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system information"""
    loader = get_data_loader()
    
    # Get system info
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    health_info = {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "loaded": loader.is_loaded,
            "last_loaded": loader.last_loaded.isoformat() if loader.last_loaded else None,
            "species_available": loader.get_all_species() if loader.is_loaded else []
        },
        "system": {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "memory_available_mb": memory.available / 1024 / 1024
        },
        "configuration": {
            "cors_origins": settings.cors_origins,
            "api_key_required": settings.require_api_key,
            "data_path": settings.data_path,
            "cache_enabled": settings.cache_data
        }
    }
    
    return health_info