"""
Input validation utilities
"""

import re
from typing import Any, Dict, List, Optional
from email_validator import validate_email, EmailNotValidError

from app.models.schemas import SpeciesEnum
from app.core.exceptions import ValidationError


class DataValidator:
    """Validates data inputs and formats"""
    
    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate email address format
        
        Args:
            email: Email address to validate
            
        Returns:
            Normalized email address
            
        Raises:
            ValidationError: If email is invalid
        """
        try:
            # Validate and normalize email
            validation = validate_email(email, check_deliverability=False)
            return validation.email
        except EmailNotValidError as e:
            raise ValidationError(f"Invalid email address: {str(e)}")
    
    @staticmethod
    def validate_password(password: str) -> None:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Raises:
            ValidationError: If password doesn't meet requirements
        """
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long")
        
        # Optional: Add more password requirements
        # if not re.search(r'[A-Z]', password):
        #     raise ValidationError("Password must contain at least one uppercase letter")
        # if not re.search(r'[a-z]', password):
        #     raise ValidationError("Password must contain at least one lowercase letter")
        # if not re.search(r'[0-9]', password):
        #     raise ValidationError("Password must contain at least one number")
    
    @staticmethod
    def validate_species(species: str) -> str:
        """
        Validate species name
        
        Args:
            species: Species name to validate
            
        Returns:
            Normalized species name
            
        Raises:
            ValidationError: If species is invalid
        """
        try:
            species_enum = SpeciesEnum(species.lower())
            return species_enum.value
        except ValueError:
            valid_species = [s.value for s in SpeciesEnum]
            raise ValidationError(
                f"Invalid species '{species}'. Valid species are: {', '.join(valid_species)}"
            )
    
    @staticmethod
    def validate_numeric_range(
        value: float,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        field_name: str = "value"
    ) -> None:
        """
        Validate numeric value is within range
        
        Args:
            value: Value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            field_name: Name of field for error messages
            
        Raises:
            ValidationError: If value is out of range
        """
        if min_value is not None and value < min_value:
            raise ValidationError(f"{field_name} must be at least {min_value}")
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"{field_name} must be at most {max_value}")
    
    @staticmethod
    def validate_data_point(data: Dict[str, Any]) -> None:
        """
        Validate Iris data point
        
        Args:
            data: Data point to validate
            
        Raises:
            ValidationError: If data is invalid
        """
        required_fields = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species']
        
        # Check required fields
        missing_fields = set(required_fields) - set(data.keys())
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Validate numeric fields
        numeric_fields = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
        for field in numeric_fields:
            try:
                value = float(data[field])
                DataValidator.validate_numeric_range(value, 0, 20, field)
            except (ValueError, TypeError):
                raise ValidationError(f"{field} must be a valid number")
        
        # Validate species
        DataValidator.validate_species(data['species'])
    
    @staticmethod
    def validate_pagination_params(limit: Optional[int], offset: Optional[int]) -> None:
        """
        Validate pagination parameters
        
        Args:
            limit: Number of records to return
            offset: Number of records to skip
            
        Raises:
            ValidationError: If parameters are invalid
        """
        if limit is not None:
            if limit < 1:
                raise ValidationError("Limit must be at least 1")
            if limit > 1000:
                raise ValidationError("Limit cannot exceed 1000")
        
        if offset is not None:
            if offset < 0:
                raise ValidationError("Offset cannot be negative")
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename for security
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        # Remove path separators and special characters
        filename = re.sub(r'[^\w\s.-]', '', filename)
        filename = filename.strip()
        
        # Ensure it has .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        return filename


class AccessValidator:
    """Validates access permissions"""
    
    @staticmethod
    def validate_species_access(user_access: str, requested_species: str) -> bool:
        """
        Check if user has access to requested species
        
        Args:
            user_access: User's access level
            requested_species: Species being requested
            
        Returns:
            True if access allowed, False otherwise
        """
        if user_access == "all":  # Admin access
            return True
        
        return user_access.lower() == requested_species.lower()
    
    @staticmethod
    def validate_admin_access(user_access: str) -> bool:
        """
        Check if user has admin access
        
        Args:
            user_access: User's access level
            
        Returns:
            True if user is admin, False otherwise
        """
        return user_access == "all"
    
    @staticmethod
    def get_accessible_species(user_access: str) -> List[str]:
        """
        Get list of species accessible to user
        
        Args:
            user_access: User's access level
            
        Returns:
            List of accessible species
        """
        if user_access == "all":
            return [s.value for s in SpeciesEnum]
        
        return [user_access]