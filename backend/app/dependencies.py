"""
FastAPI dependencies for request validation and authentication
"""

from fastapi import Header, HTTPException, status
from typing import Optional
import logging

from .config import settings

logger = logging.getLogger(__name__)


async def get_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> Optional[str]:
    """
    Validate API key if required
    
    Args:
        x_api_key: API key from header
        
    Returns:
        API key or None
        
    Raises:
        HTTPException: If API key is required but invalid
    """
    if not settings.require_api_key:
        return None
    
    if not x_api_key:
        logger.warning("API key required but not provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if x_api_key != settings.api_key:
        logger.warning(f"Invalid API key attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return x_api_key


async def require_admin_key(
    x_api_key: Optional[str] = Header(None, alias="X-Admin-Key")
) -> str:
    """
    Require admin API key for sensitive operations
    
    Args:
        x_api_key: Admin API key from header
        
    Returns:
        Admin API key
        
    Raises:
        HTTPException: If admin key is invalid
    """
    admin_key = settings.api_key or "admin-secret-key"
    
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if x_api_key != admin_key:
        logger.warning(f"Invalid admin API key attempt")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin API key"
        )
    
    return x_api_key