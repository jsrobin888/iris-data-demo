"""
Pydantic models for request/response validation
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, EmailStr
from datetime import datetime
from enum import Enum


class SpeciesEnum(str, Enum):
    """Valid Iris species"""
    SETOSA = "setosa"
    VIRGINICA = "virginica"
    VERSICOLOR = "versicolor"


class UserAccessEnum(str, Enum):
    """User access levels"""
    SETOSA = "setosa"
    VIRGINICA = "virginica"
    VERSICOLOR = "versicolor"
    ALL = "all"  # Admin access to all species


# Authentication Models
class UserCreate(BaseModel):
    """User registration model"""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    full_name: Optional[str] = None
    access_level: Optional[UserAccessEnum] = UserAccessEnum.SETOSA


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


class UserResponse(BaseModel):
    """User response model"""
    id: int
    email: str
    full_name: Optional[str]
    access_level: UserAccessEnum
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserInToken(BaseModel):
    """User data stored in JWT token"""
    user_id: int
    email: str
    access_level: str
    
    
# Data Models
class IrisDataPoint(BaseModel):
    """Single Iris data point"""
    sepal_length: float = Field(..., ge=0, description="Sepal length in cm")
    sepal_width: float = Field(..., ge=0, description="Sepal width in cm")
    petal_length: float = Field(..., ge=0, description="Petal length in cm")
    petal_width: float = Field(..., ge=0, description="Petal width in cm")
    species: SpeciesEnum


class IrisDataResponse(BaseModel):
    """Response model for Iris data"""
    species: str = Field(..., description="Species name")
    data: List[IrisDataPoint] = Field(..., description="Array of data points")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    @validator('data')
    def validate_data(cls, v):
        """Ensure data is not empty"""
        if not v:
            raise ValueError("Data array cannot be empty")
        return v


class DataStatistics(BaseModel):
    """Statistical summary of data"""
    species: str
    count: int
    sepal_length_mean: float
    sepal_width_mean: float
    petal_length_mean: float
    petal_width_mean: float
    sepal_length_std: float
    sepal_width_std: float
    petal_length_std: float
    petal_width_std: float


class DataSummaryResponse(BaseModel):
    """Summary response for accessible species"""
    total_records: int
    accessible_species: List[str]
    species_count: Dict[str, int]
    statistics: List[DataStatistics]
    last_updated: Optional[datetime] = None
    user_access_level: Optional[str] 


class DataQueryParams(BaseModel):
    """Query parameters for data endpoints"""
    normalize: bool = False
    remove_outliers: bool = False
    include_statistics: bool = True
    limit: Optional[int] = Field(None, ge=1, le=1000)
    offset: Optional[int] = Field(None, ge=0)


# Health Check Models
class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy", description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data_loaded: bool = Field(default=False, description="Whether data is loaded")
    

class DetailedHealthResponse(HealthResponse):
    """Detailed health check response"""
    system: Dict[str, Any]
    configuration: Dict[str, Any]
    data_info: Dict[str, Any]


# Error Models
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
    

# Admin Models
class DataReloadResponse(BaseModel):
    """Response for data reload operation"""
    message: str
    rows_loaded: int
    species_found: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AdminStatsResponse(BaseModel):
    """Admin statistics response"""
    total_users: int
    active_users: int
    species_access_distribution: Dict[str, int]
    api_calls_today: int
    data_last_updated: Optional[datetime]
    system_health: str