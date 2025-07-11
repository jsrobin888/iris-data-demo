"""
FastAPI dependencies for request validation and authentication
"""

from fastapi import Header, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from app.config import settings
from app.core.security import verify_access_token
from app.models.schemas import UserInToken

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


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


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInToken:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        Current user information
        
    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    try:
        user = verify_access_token(token)
        return user
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: UserInToken = Depends(get_current_user)
) -> UserInToken:
    """
    Verify user is active
    
    Args:
        current_user: Current user from token
        
    Returns:
        Active user information
        
    Raises:
        HTTPException: If user is inactive
    """
    # In a real app, you would check the database here
    # For now, we'll assume all authenticated users are active
    return current_user


async def require_admin_user(
    current_user: UserInToken = Depends(get_current_active_user)
) -> UserInToken:
    """
    Require admin access level
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Admin user information
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.access_level != "all":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[UserInToken]:
    """
    Get current user if authenticated, otherwise None
    
    Args:
        credentials: Optional HTTP Bearer token credentials
        
    Returns:
        Current user or None
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = verify_access_token(token)
        return user
    except Exception:
        return None


class RateLimitDependency:
    """Rate limiting dependency"""
    
    def __init__(self, requests: int = 100, period: int = 60):
        self.requests = requests
        self.period = period
        self.cache = {}  # In production, use Redis or similar
    
    async def __call__(self, current_user: Optional[UserInToken] = Depends(get_optional_user)):
        """Check rate limit"""
        if not settings.rate_limit_enabled:
            return
        
        # Use user ID or "anonymous" as key
        key = f"user:{current_user.user_id}" if current_user else "anonymous"
        
        # Simple in-memory rate limiting (use Redis in production)
        # This is a placeholder implementation
        return


# Create rate limiter instances
rate_limit_default = RateLimitDependency(
    requests=settings.rate_limit_requests,
    period=settings.rate_limit_period
)

rate_limit_strict = RateLimitDependency(
    requests=10,
    period=60
)