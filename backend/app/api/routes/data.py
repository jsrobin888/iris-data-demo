"""
Data endpoints with user-based access control
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional, Dict, Any
import logging

from app.models.schemas import (
    IrisDataResponse, DataSummaryResponse, SpeciesEnum,
    UserInToken, DataQueryParams, ErrorResponse
)
from app.data.loader import get_data_loader
from app.data.processor import IrisDataProcessor
from app.dependencies import get_current_active_user, rate_limit_default
from app.core.security import check_user_access
from app.core.exceptions import DataNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data")

@router.get("/", response_model=DataSummaryResponse)
async def get_data_summary(
    current_user: UserInToken = Depends(get_current_active_user),
    _: None = Depends(rate_limit_default)
) -> DataSummaryResponse:
    """
    Get summary of accessible data based on user permissions
    
    - Users with specific species access see only their species
    - Admin users (access_level: all) see all species
    """
    try:
        loader = get_data_loader()
        df = loader.load_data()
        
        # Filter based on user access
        if current_user.access_level != "all":
            # Filter to only user's accessible species
            df = df[df['species'] == current_user.access_level]
            accessible_species = [current_user.access_level]
        else:
            # Admin sees all
            accessible_species = loader.get_all_species()
        
        # Process summary
        summary = IrisDataProcessor.process_summary_data(df, loader.last_loaded)
        
        # Add user access info
        summary_dict = summary.dict()
        summary_dict['accessible_species'] = accessible_species
        summary_dict['user_access_level'] = current_user.access_level
        # REMOVE THIS LINE: summary_dict['user_access_level'] = "all"
        
        return DataSummaryResponse(**summary_dict)
        
    except Exception as e:
        logger.error(f"Error getting data summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve data summary"
        )
        

@router.get("/species/list", response_model=List[str])
async def list_accessible_species(
    current_user: UserInToken = Depends(get_current_active_user)
) -> List[str]:
    """
    List species accessible to the current user
    """
    if current_user.access_level == "all":
        loader = get_data_loader()
        return loader.get_all_species()
    else:
        return [current_user.access_level]


@router.get("/species/{species_name}", response_model=IrisDataResponse)
async def get_species_data(
    species_name: str,
    normalize: bool = Query(False, description="Normalize the data"),
    remove_outliers: bool = Query(False, description="Remove outliers"),
    include_statistics: bool = Query(True, description="Include statistics in metadata"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of records"),
    offset: Optional[int] = Query(None, ge=0, description="Offset for pagination"),
    current_user: UserInToken = Depends(get_current_active_user),
    _: None = Depends(rate_limit_default)
) -> IrisDataResponse:
    """
    Get data for a specific species
    
    Access control:
    - Users can only access their assigned species
    - Admin users can access all species
    """
    try:
        # Validate species
        try:
            species_enum = SpeciesEnum(species_name.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid species: {species_name}. Valid species are: {', '.join([s.value for s in SpeciesEnum])}"
            )
        
        # Check user access
        if not check_user_access(current_user.access_level, species_enum.value):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have access to {species_name} data. Your access level: {current_user.access_level}"
            )
        
        # Load data
        loader = get_data_loader()
        df = loader.get_species_data(species_enum.value)
        
        # Apply transformations
        if remove_outliers:
            df = IrisDataProcessor.filter_outliers(
                df, 
                ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
            )
        
        if normalize:
            df = IrisDataProcessor.normalize_data(
                df,
                ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
            )
        
        # Apply pagination
        if offset is not None:
            df = df.iloc[offset:]
        if limit is not None:
            df = df.iloc[:limit]
        
        # Process response
        response = IrisDataProcessor.process_species_data(df, species_enum.value)
        
        # Add user access info to metadata
        if response.metadata is None:
            response.metadata = {}
        response.metadata['user_access_level'] = current_user.access_level
        response.metadata['transformations'] = {
            'normalized': normalize,
            'outliers_removed': remove_outliers,
            'pagination': {
                'limit': limit,
                'offset': offset
            }
        }
        
        # Add statistics if requested
        if include_statistics:
            stats = IrisDataProcessor.calculate_statistics(df, species_enum.value)
            response.metadata['statistics'] = stats.dict()
        
        return response
        
    except DataNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving species data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve species data"
        )


@router.get("/my-data", response_model=IrisDataResponse)
async def get_my_data(
    normalize: bool = Query(False, description="Normalize the data"),
    remove_outliers: bool = Query(False, description="Remove outliers"),
    current_user: UserInToken = Depends(get_current_active_user),
    _: None = Depends(rate_limit_default)
) -> IrisDataResponse:
    """
    Get data for the user's assigned species
    
    This is a convenience endpoint that automatically uses the user's access level
    """
    if current_user.access_level == "all":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin users must specify a species. Use /api/v1/data/species/{species_name} endpoint."
        )
    
    # Redirect to species endpoint with user's access level
    return await get_species_data(
        species_name=current_user.access_level,
        normalize=normalize,
        remove_outliers=remove_outliers,
        include_statistics=True,
        limit=None,
        offset=None,
        current_user=current_user,
        _=_
    )


@router.get("/statistics", response_model=Dict[str, Any])
async def get_statistics(
    species: Optional[str] = Query(None, description="Filter by species"),
    current_user: UserInToken = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get detailed statistics for accessible data
    """
    try:
        loader = get_data_loader()
        
        if species:
            # Check access to specific species
            if not check_user_access(current_user.access_level, species):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"You don't have access to {species} data"
                )
            
            df = loader.get_species_data(species)
            stats = IrisDataProcessor.aggregate_by_species(df)
            return stats
        else:
            # Get statistics for all accessible species
            all_stats = {}
            
            if current_user.access_level == "all":
                # Admin gets all species
                df = loader.load_data()
                all_stats = IrisDataProcessor.aggregate_by_species(df)
            else:
                # Regular user gets only their species
                df = loader.get_species_data(current_user.access_level)
                stats = IrisDataProcessor.aggregate_by_species(df)
                all_stats = {current_user.access_level: stats[current_user.access_level]}
            
            return all_stats
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate statistics"
        )