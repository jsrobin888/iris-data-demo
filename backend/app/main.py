"""
Iris Data API - Main Application
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from .config import settings
from .api.routes import auth, data, health, admin
from .data.loader import get_data_loader
from .core.exceptions import IrisAPIException
from .models.schemas import ErrorResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Preload data if configured
    if settings.cache_data:
        try:
            loader = get_data_loader(settings.data_path)
            loader.load_data()
            logger.info("Data preloaded successfully")
        except Exception as e:
            logger.error(f"Failed to preload data: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="RESTful API for Iris dataset with user-based access control",
    lifespan=lifespan,
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Security
security = HTTPBearer()


# Exception handlers
@app.exception_handler(IrisAPIException)
async def iris_exception_handler(request: Request, exc: IrisAPIException):
    """Handle custom Iris API exceptions"""
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            detail=str(exc)
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            detail="An unexpected error occurred"
        ).dict()
    )


# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix=settings.api_prefix, tags=["authentication"])
app.include_router(data.router, prefix=settings.api_prefix, tags=["data"])
app.include_router(admin.router, prefix=settings.api_prefix, tags=["admin"])


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Iris Data API - View API documentation at /docs",
        "endpoints": {
            "health": "/health",
            "auth": f"{settings.api_prefix}/auth",
            "data": f"{settings.api_prefix}/data",
            "admin": f"{settings.api_prefix}/admin",
            "docs": "/docs" if settings.enable_docs else None,
            "openapi": "/openapi.json" if settings.enable_docs else None
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )