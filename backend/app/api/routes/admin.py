"""
Admin routes for data management
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Optional
import logging
import pandas as pd
from io import StringIO

from ...models.schemas import DataReloadResponse, ErrorResponse
from ...data.loader import get_data_loader
from ...config import settings
from ...dependencies import require_admin_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/reload-data", response_model=DataReloadResponse)
async def reload_data(
    admin_key: str = Depends(require_admin_key)
) -> DataReloadResponse:
    """
    Reload data from the configured data source
    
    Requires admin API key
    """
    try:
        loader = get_data_loader()
        df = loader.load_data(force_reload=True)
        
        species_list = loader.get_all_species()
        
        return DataReloadResponse(
            message="Data reloaded successfully",
            rows_loaded=len(df),
            species_found=species_list
        )
        
    except Exception as e:
        logger.error(f"Error reloading data: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to reload data: {str(e)}"
        )


@router.post("/upload-data", response_model=DataReloadResponse)
async def upload_data(
    file: UploadFile = File(..., description="CSV file with Iris data"),
    admin_key: str = Depends(require_admin_key)
) -> DataReloadResponse:
    """
    Upload new data from CSV file
    
    Requires admin API key
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are supported"
            )
        
        # Read file content
        content = await file.read()
        df = pd.read_csv(StringIO(content.decode('utf-8')))
        
        # Validate columns
        required_cols = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species']
        missing = set(required_cols) - set(df.columns)
        
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {missing}"
            )
        
        # Save to data path
        df.to_csv(settings.data_path, index=False)
        
        # Reload data
        loader = get_data_loader()
        loader.load_data(force_reload=True)
        
        return DataReloadResponse(
            message="Data uploaded and loaded successfully",
            rows_loaded=len(df),
            species_found=df['species'].unique().tolist()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload data: {str(e)}"
        )


@router.delete("/clear-cache")
async def clear_cache(
    admin_key: str = Depends(require_admin_key)
):
    """Clear data cache"""
    try:
        loader = get_data_loader()
        loader._data = None
        loader._last_loaded = None
        
        return {"message": "Cache cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clear cache"
        )


@router.get("/config")
async def get_configuration(
    admin_key: str = Depends(require_admin_key)
):
    """Get current configuration (admin only)"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "data_path": settings.data_path,
        "cache_enabled": settings.cache_data,
        "cors_origins": settings.cors_origins,
        "max_data_points": settings.max_data_points,
        "log_level": settings.log_level
    }