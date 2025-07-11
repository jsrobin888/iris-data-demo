"""
Data loading utilities for Iris dataset
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
from threading import Lock

from app.models.schemas import SpeciesEnum
from app.core.exceptions import DataLoadError, DataNotFoundError

logger = logging.getLogger(__name__)


class IrisDataLoader:
    """Handles loading and caching of Iris dataset"""
    
    def __init__(self, data_path: str = "data/iris.csv"):
        self.data_path = Path(data_path)
        self._data: Optional[pd.DataFrame] = None
        self._last_loaded: Optional[datetime] = None
        self._lock = Lock()  # Thread safety for data loading
        self._sample_data = self._get_sample_data()
        self._data_stats: Optional[Dict[str, Any]] = None
    
    @property
    def is_loaded(self) -> bool:
        """Check if data is loaded"""
        return self._data is not None
    
    @property
    def last_loaded(self) -> Optional[datetime]:
        """Get last load timestamp"""
        return self._last_loaded
    
    @property
    def data_stats(self) -> Optional[Dict[str, Any]]:
        """Get cached data statistics"""
        return self._data_stats
    
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
        with self._lock:
            if self._data is not None and not force_reload:
                logger.debug("Using cached data")
                return self._data.copy()
            
            try:
                if self.data_path.exists():
                    logger.info(f"Loading data from {self.data_path}")
                    self._data = pd.read_csv(self.data_path)
                    self._data = self._validate_data(self._data)  # Update to capture returned df
                    self._last_loaded = datetime.utcnow()
                    self._calculate_stats()
                    logger.info(f"Loaded {len(self._data)} records from CSV")
                else:
                    logger.warning(f"Data file not found at {self.data_path}, using sample data")
                    self._data = self._sample_data.copy()
                    self._last_loaded = datetime.utcnow()
                    self._calculate_stats()
                
                return self._data.copy()
                
            except pd.errors.EmptyDataError:
                raise DataLoadError("CSV file is empty")
            except pd.errors.ParserError as e:
                raise DataLoadError(f"Failed to parse CSV: {str(e)}")
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
            valid_species = self.get_all_species()
            raise DataNotFoundError(
                f"Invalid species: {species}. Valid species are: {', '.join(valid_species)}"
            )
        
        # Filter data
        filtered = self._data[self._data['species'] == species_enum.value].copy()
        
        if filtered.empty:
            # Try case-insensitive match
            filtered = self._data[
                self._data['species'].str.lower() == species.lower()
            ].copy()
        
        if filtered.empty:
            raise DataNotFoundError(f"No data found for species: {species}")
        
        return filtered
    
    def get_all_species(self) -> List[str]:
        """Get list of all available species"""
        if not self.is_loaded:
            self.load_data()
        
        return sorted(self._data['species'].unique().tolist())
    
    def get_species_count(self) -> Dict[str, int]:
        """Get count of records per species"""
        if not self.is_loaded:
            self.load_data()
        
        return self._data['species'].value_counts().to_dict()
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics for all species"""
        if not self.is_loaded:
            self.load_data()
        
        return self._data_stats or self._calculate_stats()
    
    def validate_species_access(self, species: str, user_access: str) -> bool:
        """
        Validate if user has access to species
        
        Args:
            species: Species to access
            user_access: User's access level
            
        Returns:
            True if access allowed, False otherwise
        """
        if user_access == "all":  # Admin access
            return True
        
        return species.lower() == user_access.lower()
    
    def _calculate_stats(self) -> Dict[str, Any]:
        """Calculate and cache data statistics"""
        if self._data is None:
            return {}
        
        summary = {
            'total_records': len(self._data),
            'species_distribution': self.get_species_count(),
            'features': {}
        }
        
        # Calculate statistics for each numeric column
        numeric_cols = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
        
        for col in numeric_cols:
            summary['features'][col] = {
                'mean': float(self._data[col].mean()),
                'std': float(self._data[col].std()),
                'min': float(self._data[col].min()),
                'max': float(self._data[col].max()),
                'median': float(self._data[col].median()),
                'q1': float(self._data[col].quantile(0.25)),
                'q3': float(self._data[col].quantile(0.75))
            }
        
        # Calculate per-species statistics
        summary['species_stats'] = {}
        for species in self._data['species'].unique():
            species_data = self._data[self._data['species'] == species]
            summary['species_stats'][species] = {
                'count': len(species_data),
                'features': {}
            }
            
            for col in numeric_cols:
                summary['species_stats'][species]['features'][col] = {
                    'mean': float(species_data[col].mean()),
                    'std': float(species_data[col].std())
                }
        
        self._data_stats = summary
        return summary
    
    # In loader.py, update the _validate_data method (around line 190):

    
    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate loaded DataFrame has required columns and proper data types"""
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
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    # Check for NaN values after conversion
                    if df[col].isna().any():
                        raise DataLoadError(f"Column {col} contains non-numeric values")
                except Exception as e:
                    raise DataLoadError(f"Column {col} must be numeric: {str(e)}")
        
        # Clean species names - remove "Iris-" prefix if present
        df['species'] = df['species'].str.lower().str.replace('iris-', '', regex=False)
        
        # Validate species values
        valid_species = [s.value for s in SpeciesEnum]
        invalid_species = set(df['species'].unique()) - set(valid_species)
        if invalid_species:
            logger.warning(f"Found invalid species after cleaning: {invalid_species}")
            # Filter out invalid species
            df = df[df['species'].isin(valid_species)]
            if df.empty:
                raise DataLoadError("No valid species found in data")
        
        # Check for minimum data requirements
        if len(df) < 1:
            raise DataLoadError("Dataset must contain at least one record")
        
        # Check for missing values
        if df.isnull().any().any():
            logger.warning("Dataset contains missing values, dropping rows with NaN")
            df = df.dropna()
        
        return df  # Return the cleaned dataframe
    
    def _get_sample_data(self) -> pd.DataFrame:
        """Generate comprehensive sample Iris data for demo purposes"""
        return pd.DataFrame({
            'sepal_length': [
                # Setosa (20 samples)
                5.1, 4.9, 4.7, 4.6, 5.0, 5.4, 4.6, 5.0, 4.4, 4.9,
                5.4, 4.8, 4.8, 4.3, 5.8, 5.7, 5.4, 5.1, 5.7, 5.1,
                # Versicolor (20 samples)
                7.0, 6.4, 6.9, 5.5, 6.5, 5.7, 6.3, 4.9, 6.6, 5.2,
                5.0, 5.9, 6.0, 6.1, 5.6, 6.7, 5.6, 5.8, 6.2, 5.6,
                # Virginica (20 samples)
                6.3, 5.8, 7.1, 6.3, 6.5, 7.6, 4.9, 7.3, 6.7, 7.2,
                6.5, 6.4, 6.8, 5.7, 5.8, 6.4, 6.5, 7.7, 7.7, 6.0
            ],
            'sepal_width': [
                # Setosa
                3.5, 3.0, 3.2, 3.1, 3.6, 3.9, 3.4, 3.4, 2.9, 3.1,
                3.7, 3.4, 3.0, 3.0, 4.0, 4.4, 3.9, 3.5, 3.8, 3.8,
                # Versicolor
                3.2, 3.2, 3.1, 2.3, 2.8, 2.8, 3.3, 2.4, 2.9, 2.7,
                2.0, 3.0, 2.2, 2.9, 2.9, 3.1, 3.0, 2.7, 2.2, 2.5,
                # Virginica
                3.3, 2.7, 3.0, 2.9, 3.0, 3.0, 2.5, 2.9, 2.5, 3.6,
                3.2, 2.7, 3.0, 2.5, 2.8, 3.2, 3.0, 3.8, 2.6, 2.2
            ],
            'petal_length': [
                # Setosa
                1.4, 1.4, 1.3, 1.5, 1.4, 1.7, 1.4, 1.5, 1.4, 1.5,
                1.5, 1.6, 1.4, 1.1, 1.2, 1.5, 1.3, 1.4, 1.7, 1.5,
                # Versicolor
                4.7, 4.5, 4.9, 4.0, 4.6, 4.5, 4.7, 3.3, 4.6, 3.9,
                3.5, 4.2, 4.0, 4.7, 3.6, 4.4, 4.5, 4.1, 4.5, 3.9,
                # Virginica
                6.0, 5.1, 5.9, 5.6, 5.8, 6.6, 4.5, 6.3, 5.8, 6.1,
                5.1, 5.3, 5.5, 5.0, 5.1, 5.3, 5.5, 6.7, 6.9, 5.0
            ],
            'petal_width': [
                # Setosa
                0.2, 0.2, 0.2, 0.2, 0.2, 0.4, 0.3, 0.2, 0.2, 0.1,
                0.2, 0.2, 0.1, 0.1, 0.2, 0.4, 0.4, 0.3, 0.3, 0.3,
                # Versicolor
                1.4, 1.5, 1.5, 1.3, 1.5, 1.3, 1.6, 1.0, 1.3, 1.4,
                1.0, 1.5, 1.2, 1.4, 1.3, 1.4, 1.5, 1.0, 1.5, 1.1,
                # Virginica
                2.5, 1.9, 2.1, 1.8, 2.2, 2.1, 1.7, 1.8, 1.8, 2.5,
                2.0, 1.9, 2.1, 2.0, 2.4, 2.3, 1.8, 2.2, 2.3, 1.5
            ],
            'species': (
                ['setosa'] * 20 +
                ['versicolor'] * 20 +
                ['virginica'] * 20
            )
        })


# Global loader instance
_loader: Optional[IrisDataLoader] = None


def get_data_loader(data_path: Optional[str] = None) -> IrisDataLoader:
    """Get or create data loader instance"""
    global _loader
    
    if _loader is None or data_path is not None:
        from app.config import settings
        path = data_path or settings.data_path
        _loader = IrisDataLoader(path)
    
    return _loader