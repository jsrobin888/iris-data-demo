"""
Authentication routes - app/api/routes/auth.py
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any
import logging
from datetime import datetime

from app.models.schemas import (
    UserCreate, UserLogin, UserResponse, Token, 
    TokenRefresh, ErrorResponse, UserInToken
)
from app.core.security import (
    hash_password, verify_password, create_tokens, 
    verify_refresh_token
)
from app.dependencies import get_current_active_user

logger = logging.getLogger(__name__)

# IMPORTANT: Create the router instance
router = APIRouter(prefix="/auth")

# Temporary in-memory user storage (replace with database in production)
users_db: Dict[str, Dict[str, Any]] = {
    "setosa@example.com": {
        "id": 1,
        "email": "setosa@example.com",
        "password": hash_password("password123"),
        "full_name": "Setosa User",
        "access_level": "setosa",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    },
    "virginica@example.com": {
        "id": 2,
        "email": "virginica@example.com",
        "password": hash_password("password123"),
        "full_name": "Virginica User",
        "access_level": "virginica",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    },
    "admin@example.com": {
        "id": 3,
        "email": "admin@example.com",
        "password": hash_password("admin123"),
        "full_name": "Admin User",
        "access_level": "all",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
}

# Counter for new user IDs
next_user_id = 4


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    global next_user_id
    
    if user_data.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    user_id = next_user_id
    next_user_id += 1
    
    new_user = {
        "id": user_id,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "access_level": user_data.access_level or "setosa",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
    
    users_db[user_data.email] = new_user
    
    return UserResponse(**new_user)


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login with email and password"""
    user = users_db.get(credentials.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    tokens = create_tokens(
        user_id=user["id"],
        email=user["email"],
        access_level=user["access_level"]
    )
    
    logger.info(f"User {user['email']} logged in successfully")
    
    return Token(**tokens)


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_data: TokenRefresh):
    """Refresh access token using refresh token"""
    try:
        user_info = verify_refresh_token(refresh_data.refresh_token)
        
        user = None
        for email, user_data in users_db.items():
            if user_data["id"] == user_info.user_id:
                user = user_data
                break
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        tokens = create_tokens(
            user_id=user["id"],
            email=user["email"],
            access_level=user["access_level"]
        )
        
        return Token(**tokens)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserInToken = Depends(get_current_active_user)
):
    """Get current user information"""
    user = None
    for email, user_data in users_db.items():
        if user_data["id"] == current_user.user_id:
            user = user_data
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user)


@router.post("/logout")
async def logout(
    current_user: UserInToken = Depends(get_current_active_user)
):
    """Logout current user"""
    logger.info(f"User {current_user.email} logged out")
    return {"message": "Successfully logged out"}