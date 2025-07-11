"""
Data processing utilities for transforming Iris data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging

from ..models.schemas import IrisDataResponse, DataStatistics, DataSummaryResponse

logger = logging.getLogger(__name__)


class IrisDataProcessor:
    """Processes and transforms Iris data for API responses"""
    
    @staticmethod
    def process_species_data(df: pd.DataFrame, species: str) -> IrisDataResponse:
        """
        Process species data into API response format
        
        Args:
            df: DataFrame with species data
            species: Species name
            
        Returns:
            IrisDataResponse object
        """
        # Convert DataFrame rows to list of dictionaries
        data_points = []
        for _, row in df.iterrows():
            data_points.append({
                'sepal_length': float(row['sepal_length']),
                'sepal_width': float(row['sepal_width']),
                'petal_length': float(row['petal_length']),
                'petal_width': float(row['petal_width']),
                'species': species 
            })
        
        response_data = {
            'species': species,
            'data': data_points,
            'metadata': {
                'count': len(df),
                'min_values': {
                    'sepal_length': float(df['sepal_length'].min()),
                    'sepal_width': float(df['sepal_width'].min()),
                    'petal_length': float(df['petal_length'].min()),
                    'petal_width': float(df['petal_width'].min())
                },
                'max_values': {
                    'sepal_length': float(df['sepal_length'].max()),
                    'sepal_width': float(df['sepal_width'].max()),
                    'petal_length': float(df['petal_length'].max()),
                    'petal_width': float(df['petal_width'].max())
                }
            }
        }
    
        return IrisDataResponse(**response_data)

    @staticmethod
    def calculate_statistics(df: pd.DataFrame, species: str) -> DataStatistics:
        """
        Calculate statistics for a species
        
        Args:
            df: DataFrame with species data
            species: Species name
            
        Returns:
            DataStatistics object
        """
        stats = {
            'species': species,
            'count': len(df)
        }
        
        # Calculate mean and std for each measurement
        for col in ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']:
            stats[f'{col}_mean'] = float(df[col].mean())
            stats[f'{col}_std'] = float(df[col].std())
        
        return DataStatistics(**stats)
    
    @staticmethod
    def process_summary_data(df: pd.DataFrame, last_updated: Optional[Any] = None) -> DataSummaryResponse:
        """
        Process full dataset into summary response
        
        Args:
            df: Full dataset DataFrame
            last_updated: Last update timestamp
            
        Returns:
            DataSummaryResponse object
        """
        # Calculate species counts
        species_counts = df['species'].value_counts().to_dict()
        
        # Calculate statistics for each species
        statistics = []
        for species in df['species'].unique():
            species_df = df[df['species'] == species]
            stats = IrisDataProcessor.calculate_statistics(species_df, species)
            statistics.append(stats)
        
        return DataSummaryResponse(
            total_records=len(df),
            species_count=species_counts,
            statistics=statistics,
            last_updated=last_updated
        )
    
    @staticmethod
    def filter_outliers(df: pd.DataFrame, columns: List[str], n_std: float = 3.0) -> pd.DataFrame:
        """
        Filter outliers from data using z-score method
        
        Args:
            df: Input DataFrame
            columns: Columns to check for outliers
            n_std: Number of standard deviations for outlier threshold
            
        Returns:
            DataFrame with outliers removed
        """
        df_filtered = df.copy()
        
        for col in columns:
            if col in df.columns:
                mean = df[col].mean()
                std = df[col].std()
                
                # Calculate z-scores
                z_scores = np.abs((df[col] - mean) / std)
                
                # Filter outliers
                df_filtered = df_filtered[z_scores <= n_std]
                
                removed = len(df) - len(df_filtered)
                if removed > 0:
                    logger.info(f"Removed {removed} outliers from {col}")
        
        return df_filtered
    
    @staticmethod
    def normalize_data(df: pd.DataFrame, columns: List[str], method: str = 'minmax') -> pd.DataFrame:
        """
        Normalize numeric columns
        
        Args:
            df: Input DataFrame
            columns: Columns to normalize
            method: Normalization method ('minmax' or 'zscore')
            
        Returns:
            DataFrame with normalized columns
        """
        df_normalized = df.copy()
        
        for col in columns:
            if col in df.columns:
                if method == 'minmax':
                    # Min-Max normalization
                    min_val = df[col].min()
                    max_val = df[col].max()
                    df_normalized[f'{col}_normalized'] = (df[col] - min_val) / (max_val - min_val)
                elif method == 'zscore':
                    # Z-score normalization
                    mean = df[col].mean()
                    std = df[col].std()
                    df_normalized[f'{col}_normalized'] = (df[col] - mean) / std
        
        return df_normalized
    
    @staticmethod
    def aggregate_by_species(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Aggregate data by species with various statistics
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with aggregated statistics per species
        """
        aggregations = {}
        
        for species in df['species'].unique():
            species_df = df[df['species'] == species]
            
            agg_stats = {}
            for col in ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']:
                agg_stats[col] = {
                    'mean': float(species_df[col].mean()),
                    'median': float(species_df[col].median()),
                    'std': float(species_df[col].std()),
                    'min': float(species_df[col].min()),
                    'max': float(species_df[col].max()),
                    'q25': float(species_df[col].quantile(0.25)),
                    'q75': float(species_df[col].quantile(0.75))
                }
            
            aggregations[species] = agg_stats
        
        return aggregations