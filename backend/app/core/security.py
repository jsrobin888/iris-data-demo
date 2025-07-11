"""
Security utilities for authentication and authorization
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import logging

from app.config import settings
from app.models.schemas import UserInToken

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    """Handles all security operations"""
    
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        self.refresh_token_expire = timedelta(days=settings.jwt_refresh_token_expire_days)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + self.access_token_expire
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + self.refresh_token_expire
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.error(f"JWT decode error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def verify_token(self, token: str, token_type: str = "access") -> UserInToken:
        """Verify token and extract user information"""
        payload = self.decode_token(token)
        
        # Check token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract user info
        user_id = payload.get("sub")
        email = payload.get("email")
        access_level = payload.get("access_level")
        
        if not all([user_id, email, access_level]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return UserInToken(
            user_id=int(user_id),
            email=email,
            access_level=access_level
        )
    
    def create_tokens(self, user_id: int, email: str, access_level: str) -> Dict[str, str]:
        """Create both access and refresh tokens"""
        token_data = {
            "sub": str(user_id),
            "email": email,
            "access_level": access_level
        }
        
        return {
            "access_token": self.create_access_token(token_data),
            "refresh_token": self.create_refresh_token(token_data),
            "token_type": "bearer",
            "expires_in": int(self.access_token_expire.total_seconds())
        }


# Global instance
security_manager = SecurityManager()


# Utility functions
def hash_password(password: str) -> str:
    """Hash a password"""
    return security_manager.get_password_hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return security_manager.verify_password(plain_password, hashed_password)


def create_tokens(user_id: int, email: str, access_level: str) -> Dict[str, str]:
    """Create JWT tokens for a user"""
    return security_manager.create_tokens(user_id, email, access_level)


def verify_access_token(token: str) -> UserInToken:
    """Verify an access token"""
    return security_manager.verify_token(token, "access")


def verify_refresh_token(token: str) -> UserInToken:
    """Verify a refresh token"""
    return security_manager.verify_token(token, "refresh")


def check_user_access(user_access: str, required_species: str) -> bool:
    """Check if user has access to a specific species"""
    if user_access == "all":  # Admin access
        return True
    
    if user_access == required_species:
        return True
    
    return False