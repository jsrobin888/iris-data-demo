"""
Data loading utilities for Iris dataset
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from ..models.schemas import SpeciesEnum
from ..core.exceptions import DataLoadError, DataNotFoundError

logger = logging.getLogger(__name__)


class IrisDataLoader:
    """Handles loading and caching of Iris dataset"""
    
    def __init__(self, data_path: str = "data/iris.csv"):
        self.data_path = Path(data_path)
        self._data: Optional[pd.DataFrame] = None
        self._last_loaded: Optional[datetime] = None
        self._sample_data = self._get_sample_data()
    
    @property
    def is_loaded(self) -> bool:
        """Check if data is loaded"""
        return self._data is not None
    
    @property
    def last_loaded(self) -> Optional[datetime]:
        """Get last load timestamp"""
        return self._last_loaded
    
    def load_data(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Load Iris data from CSV file or use sample data
        
        Args:
            force_reload: Force reload even if data is cached
            
        Returns:
            Loaded DataFrame
            
        Raises:
            DataLoadError: If data cannot be loaded
        """
        if self._data is not None and not force_reload:
            logger.info("Using cached data")
            return self._data
        
        try:
            if self.data_path.exists():
                logger.info(f"Loading data from {self.data_path}")
                self._data = pd.read_csv(self.data_path)
                self._validate_data(self._data)
                self._last_loaded = datetime.utcnow()
                logger.info(f"Loaded {len(self._data)} records from CSV")
            else:
                logger.warning(f"Data file not found at {self.data_path}, using sample data")
                self._data = self._sample_data.copy()
                self._last_loaded = datetime.utcnow()
                
            return self._data
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise DataLoadError(f"Failed to load data: {str(e)}")
    
    def get_species_data(self, species: str) -> pd.DataFrame:
        """
        Get data for a specific species
        
        Args:
            species: Species name to filter
            
        Returns:
            Filtered DataFrame
            
        Raises:
            DataNotFoundError: If species not found
        """
        if not self.is_loaded:
            self.load_data()
        
        # Validate species
        try:
            species_enum = SpeciesEnum(species.lower())
        except ValueError:
            raise DataNotFoundError(f"Invalid species: {species}")
        
        # Filter data
        filtered = self._data[self._data['species'] == species_enum.value]
        
        if filtered.empty:
            # Try to find with case-insensitive match
            filtered = self._data[self._data['species'].str.lower() == species.lower()]
        
        if filtered.empty:
            raise DataNotFoundError(f"No data found for species: {species}")
        
        return filtered
    
    def get_all_species(self) -> list:
        """Get list of all available species"""
        if not self.is_loaded:
            self.load_data()
        
        return self._data['species'].unique().tolist()
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics for all species"""
        if not self.is_loaded:
            self.load_data()
        
        summary = {}
        for species in self._data['species'].unique():
            species_data = self._data[self._data['species'] == species]
            summary[species] = {
                'count': len(species_data),
                'statistics': {
                    col: {
                        'mean': float(species_data[col].mean()),
                        'std': float(species_data[col].std()),
                        'min': float(species_data[col].min()),
                        'max': float(species_data[col].max())
                    }
                    for col in ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
                }
            }
        
        return summary
    
    def _validate_data(self, df: pd.DataFrame) -> None:
        """Validate loaded DataFrame has required columns"""
        required_cols = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species']
        missing = set(required_cols) - set(df.columns)
        
        if missing:
            raise DataLoadError(f"Missing required columns: {missing}")
        
        # Check for numeric columns
        numeric_cols = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
        for col in numeric_cols:
            if not pd.api.types.is_numeric_dtype(df[col]):
                # Try to convert
                try:
                    df[col] = pd.to_numeric(df[col])
                except:
                    raise DataLoadError(f"Column {col} must be numeric")
    
    def _get_sample_data(self) -> pd.DataFrame:
        """Generate sample Iris data for demo purposes"""
        return pd.DataFrame({
            'sepal_length': [
                # Setosa
                5.1, 4.9, 4.7, 4.6, 5.0, 5.4, 4.6, 5.0, 4.4, 4.9,
                # Virginica
                6.3, 5.8, 7.1, 6.3, 6.5, 7.6, 4.9, 7.3, 6.7, 7.2
            ],
            'sepal_width': [
                # Setosa
                3.5, 3.0, 3.2, 3.1, 3.6, 3.9, 3.4, 3.4, 2.9, 3.1,
                # Virginica
                3.3, 2.7, 3.0, 2.9, 3.0, 3.0, 2.5, 2.9, 2.5, 3.6
            ],
            'petal_length': [
                # Setosa
                1.4, 1.4, 1.3, 1.5, 1.4, 1.7, 1.4, 1.5, 1.4, 1.5,
                # Virginica
                6.0, 5.1, 5.9, 5.6, 5.8, 6.6, 4.5, 6.3, 5.8, 6.1
            ],
            'petal_width': [
                # Setosa
                0.2, 0.2, 0.2, 0.2, 0.2, 0.4, 0.3, 0.2, 0.2, 0.1,
                # Virginica
                2.5, 1.9, 2.1, 1.8, 2.2, 2.1, 1.7, 1.8, 1.8, 2.5
            ],
            'species': ['setosa'] * 10 + ['virginica'] * 10
        })


# Global loader instance
_loader: Optional[IrisDataLoader] = None


def get_data_loader(data_path: Optional[str] = None) -> IrisDataLoader:
    """Get or create data loader instance"""
    global _loader
    
    if _loader is None or data_path is not None:
        path = data_path or "data/iris.csv"
        _loader = IrisDataLoader(path)
    
    return _loader