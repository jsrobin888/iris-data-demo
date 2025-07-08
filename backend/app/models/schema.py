"""
Pydantic models for request/response validation
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class SpeciesEnum(str, Enum):
    """Valid Iris species"""
    SETOSA = "setosa"
    VIRGINICA = "virginica"
    VERSICOLOR = "versicolor"


class IrisDataPoint(BaseModel):
    """Single Iris data point"""
    sepal_length: float = Field(..., ge=0, description="Sepal length in cm")
    sepal_width: float = Field(..., ge=0, description="Sepal width in cm")
    petal_length: float = Field(..., ge=0, description="Petal length in cm")
    petal_width: float = Field(..., ge=0, description="Petal width in cm")
    species: SpeciesEnum


class IrisDataResponse(BaseModel):
    """Response model for Iris data"""
    sepal_length: List[float] = Field(..., description="Array of sepal lengths")
    sepal_width: List[float] = Field(..., description="Array of sepal widths")
    petal_length: List[float] = Field(..., description="Array of petal lengths")
    petal_width: List[float] = Field(..., description="Array of petal widths")
    species: str = Field(..., description="Species name")
    count: int = Field(..., description="Number of data points")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    @validator('count')
    def validate_count(cls, v, values):
        """Ensure count matches data length"""
        if 'sepal_length' in values:
            expected = len(values['sepal_length'])
            if v != expected:
                raise ValueError(f"Count {v} does not match data length {expected}")
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
    """Summary response for all species"""
    total_records: int
    species_count: Dict[str, int]
    statistics: List[DataStatistics]
    last_updated: Optional[datetime] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy", description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data_loaded: bool = Field(default=False, description="Whether data is loaded")
    

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    

class DataReloadResponse(BaseModel):
    """Response for data reload operation"""
    message: str
    rows_loaded: int
    species_found: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)