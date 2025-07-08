"""
Data API routes
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
import logging

from ...models.schemas import (
    IrisDataResponse, 
    DataSummaryResponse, 
    ErrorResponse,
    SpeciesEnum
)
from ...data.loader import get_data_loader
from ...data.processor import IrisDataProcessor
from ...core.exceptions import DataNotFoundError, DataLoadError
from ...dependencies import get_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data", tags=["data"])


@router.get("/{species}", response_model=IrisDataResponse)
async def get_species_data(
    species: str,
    normalize: bool = Query(False, description="Normalize the data"),
    remove_outliers: bool = Query(False, description="Remove outliers"),
    api_key: Optional[str] = Depends(get_api_key)
) -> IrisDataResponse:
    """
    Get Iris data for a specific species
    
    - **species**: Species name (setosa, virginica, or versicolor)
    - **normalize**: Apply min-max normalization to the data
    - **remove_outliers**: Remove outliers using 3-sigma rule
    """
    try:
        # Load data
        loader = get_data_loader()
        df = loader.get_species_data(species)
        
        # Apply transformations if requested
        if remove_outliers:
            numeric_cols = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
            df = IrisDataProcessor.filter_outliers(df, numeric_cols)
            logger.info(f"Filtered outliers, {len(df)} records remaining")
        
        if normalize:
            numeric_cols = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
            df = IrisDataProcessor.normalize_data(df, numeric_cols)
            logger.info("Applied normalization to data")
        
        # Process and return data
        return IrisDataProcessor.process_species_data(df, species)
        
    except DataNotFoundError as e:
        logger.error(f"Species not found: {species}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving species data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=DataSummaryResponse)
async def get_data_summary(
    include_stats: bool = Query(True, description="Include detailed statistics"),
    api_key: Optional[str] = Depends(get_api_key)
) -> DataSummaryResponse:
    """
    Get summary statistics for all species
    
    - **include_stats**: Include detailed statistics for each species
    """
    try:
        loader = get_data_loader()
        loader.load_data()  # Ensure data is loaded
        
        # Get full dataset
        df = loader._data
        
        # Process summary
        summary = IrisDataProcessor.process_summary_data(
            df, 
            last_updated=loader.last_loaded
        )
        
        # Remove detailed stats if not requested
        if not include_stats:
            summary.statistics = []
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/species/list", response_model=List[str])
async def list_species(
    api_key: Optional[str] = Depends(get_api_key)
) -> List[str]:
    """Get list of available species"""
    try:
        loader = get_data_loader()
        return loader.get_all_species()
    except Exception as e:
        logger.error(f"Error listing species: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/aggregated/{species}")
async def get_aggregated_data(
    species: str,
    api_key: Optional[str] = Depends(get_api_key)
):
    """Get aggregated statistics for a specific species"""
    try:
        loader = get_data_loader()
        df = loader.get_species_data(species)
        
        # Get aggregated statistics
        all_aggregations = IrisDataProcessor.aggregate_by_species(df)
        
        # Return only requested species
        if species in all_aggregations:
            return {
                "species": species,
                "statistics": all_aggregations[species]
            }
        else:
            raise DataNotFoundError(f"No aggregated data for species: {species}")
            
    except DataNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting aggregated data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")